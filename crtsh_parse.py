#!/usr/bin/python3
#Inspired by @curi0usJack

import requests
import sys
import re
import argparse
import csv
import os.path
from datetime import datetime
from bs4 import BeautifulSoup

output_file = "domains.csv"

def getCerts(query):
    url = 'https://crt.sh/?q={}'.format(query)
    #print("[+] URL: " + url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    domains = {}
    for tr in soup.findAll('tr'):
        tds = tr.findAll('td')
        if len(tds) == 6:
            certid = tds[0].text
            #strenddate = tds[3].text
            #dtenddate = datetime.strptime(strenddate, "%Y-%m-%d")
            # Don't care about expired certs
            #if dtenddate > datetime.now():
            getDomains(certid,domains)

    return domains

def getDomains(certid,domains):
    url = 'https://crt.sh/?id={}'.format(certid)
    #print("[+] URL: " + url)
    r = requests.get(url)
    domain_re = re.compile(r'DNS:(.*?)<',re.M)
    domain_list = domain_re.findall(r.content.decode('utf-8'))
    domain_list = list(set([str(x).lower() for x in domain_list]))
    for domain in domain_list:
        domains[domain] = {
                "certid": certid,
                "date_found": datetime.now().strftime("%m/%d/%Y")
        }
    print("[+] CertID: " + certid + " Domains: " + str(len(domain_list)))

def checkDiff(new_domains,fieldnames):
    old_domains = []
    with open(output_file,"r") as f:
        for row in csv.DictReader(f): old_domains.append(row['domain'])
    
    print("\n[+] Domains in database: " + str(len(old_domains)))
    diff = list(set(new_domains.keys()) - set(old_domains))

    print("\n[+] New domains discovered: " + str(len(diff)))
    if diff:
        print(diff)
        with open(output_file,"a") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for domain in diff:
                print("[+] Adding domain: " + domain)
                row = {}
                row['domain'] = domain
                row['certid'] = new_domains[domain]['certid']
                row['date_found'] = new_domains[domain]['date_found']
                print(row)
                writer.writerow(row)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="(Domain Name, Organization Name, etc)", action="store")
    #parser.add_argument("-o", "--output_path", help="Output file path (e.g. /tmp/crtsh.log)", action="store")
    args = parser.parse_args()

    if args.query is None:
        print("[!] Exception. You must specify either identity <\"Company name\"> or <targetdomain.com>. Use -h for help.")
        exit(1)

    args.query = args.query.replace(" ","+")
    domains = getCerts(args.query)
    print("\n[+] Total domains found: " + str(len(domains)))
    for domain in domains: 
        print(domain + " " + domains[domain]['certid'])

    if domains is None:
        print("[-] No domains found. Exiting.")
    else:
        fieldnames = ['domain','certid','date_found']
        if not os.path.isfile(output_file):
            print("\n[*] Saving output to " + output_file)
            with open(output_file, "w") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for domain in domains:
                    row = {}
                    row['domain'] = domain
                    row['certid'] = domains[domain]['certid']
                    row['date_found'] = domains[domain]['date_found']
                    writer.writerow(row)
        else: 
            checkDiff(domains,fieldnames)

    print("\n[+] Done!\n")


if __name__ == '__main__':
    main()
