import argparse
import json
import logging
import ipaddress

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_cdn_subdomains(subdomain, cname, ips, check_cdn_func):
    return check_cdn_func(cname, ips)


def is_list(obj):
    return isinstance(obj, list)


def is_internal_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False


def get_cdn_result(host, cname, a, check_cdn_func):
    if not is_list(a):
        a = [a]
    if not is_list(cname):
        cname = [cname]

    return check_cdn_subdomains(host, cname, a, check_cdn_func)


def get_results(json_str, check_cdn_func):
    data = json.loads(json_str)

    host = data.get("host", "")
    a = data.get("a", [])
    cname = data.get("cname", [])

    cdn_result = get_cdn_result(host, cname, a, check_cdn_func)

    results = [{"subdomain": host, "CNAME": cname, "Aip": a, "cdn": cdn_result}]

    result_not_internal_subdomain = ""
    result_not_internal_ip = []
    result_cdn_tag = ""
    for result in results:
        if not any(is_internal_ip(ip) for ip in result['Aip']):
            result_not_internal_subdomain = result['subdomain']
            result_not_internal_ip.extend(result['Aip'])
            result_cdn_tag = result['cdn']

    return {"subdomain": result_not_internal_subdomain, "Aip": result_not_internal_ip, "cdn": result_cdn_tag}


def save_results_to_file(results, filename):
    with open(filename, 'w') as f:
        for result in results:
            json.dump(result, f)
            f.write('\n')

    logger.info(f"Results saved to {filename}")


def process_file(input_file, output_file, check_cdn_func):
    with open(input_file, 'r') as f:
        json_lines = f.read().splitlines()

    results = []
    for json_str in json_lines:
        result = get_results(json_str, check_cdn_func)
        if result['subdomain']:
            results.append(result)

    save_results_to_file(results, output_file)

    logging.info(f"Results saved to {output_file}")


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process DNS data')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Input file name')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output file name')
    return parser.parse_args()


def main():
    check_cdn_func = None
    try:
        from CDN.checkCDN import checkCDN
        check_cdn_func = checkCDN
    except ImportError:
        logger.warning("Cannot import checkCDN function from CDN module. CDN check will be skipped.")

    args = parse_arguments()
    input_file = args.input
    output_file = args.output

    process_file(input_file, output_file, check_cdn_func)


if __name__ == '__main__':
    main()
