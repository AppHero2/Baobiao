#!/usr/bin/env python

import argparse
import sys
import os
import csv
import re
from amazonbookquery.errors import *
from amazonbookquery.query import Query

class BookQuery:

    def _get_data(self, filepath):
        ret = []
        with open(filepath, "r", encoding="utf-8") as fd:
            reader = csv.reader(fd, delimiter="\t")
            for row in reader:
                ret.append(row)

        del ret[0]

        return ret

    def _get_transformed_author(self, data):
        if "," not in data:
            if ";" in data:
                data = data.split(";")[0]
            if "(" in data:
                data = data.split("(")[0]
        else:
            data = data.split(",")
            last_name = data[0]
            first_name = data[1]

            if ";" in data[1]:
                first_name = data[1].split(";")[0]
            if "(" in data[1]:
                first_name = data[1].split("(")[0]
            if self.hasNumbers(data[1]):
                first_name = re.search(r'(^[^\d]+)', data[1]).groups()[0]

            data = first_name + ' ' + last_name

        return data.strip()

    def hasNumbers(self, data):
        return bool(re.search(r'\d', data))

    def generate_output(self, source_file_path, output_dir):
        filename = os.path.basename(source_file_path)
        output_filename = filename[:-4] + "_output.tsv"
        datas = self._get_data(source_file_path)
        output_path = os.path.join(output_dir, output_filename)

        query = Query()

        with open(output_path, "w", encoding="utf-8", newline="") as fd:
            writer = csv.writer(fd, delimiter="\t")
            header = ['identifier', 'title', 'volume', 'creator', 'details', 'transformed_author', 'amzn-Author',
                      'amzn-Title', 'DetailPageURL', 'TotalNew', 'TotalUsed', 'TotalCollectible', 'LowestNewPrice',
                      'LowestUsedPrice', 'LowestCollectiblePrice', 'SoldByAmzn', 'SoldByAmznNew']
            writer.writerow(header)

            for data in datas:
                try:
                    row = []
                    identifier = data[0]
                    title = data[1]
                    creator = data[2]
                    volume = data[3]
                    details = data[4]
                    transformed_author = self._get_transformed_author(creator)

                    row.append(identifier)
                    row.append(title)
                    row.append(volume)
                    row.append(creator)
                    row.append(details)
                    row.append(transformed_author)

                    aws_item = query.execute_query(title, transformed_author)

                    row.append(aws_item['author'])
                    row.append(aws_item['title'])
                    row.append(aws_item['detail_page_url'])
                    row.append(aws_item['total_new'])
                    row.append(aws_item['total_used'])
                    row.append(aws_item['total_collectible'])
                    row.append(aws_item['lowest_new_price'])
                    row.append(aws_item['lowest_used_price'])
                    row.append(aws_item['lowest_collectible_price'])
                    row.append(aws_item['sold_by_amazon'])
                    row.append(aws_item['sold_by_amazon_as_new'])
                except AWSError:
                    e = sys.exc_info()[1]
                    row = [e.code, e.msg]

                print(row)
                writer.writerow(row)

        return output_path

def _parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Provide Amazon Book Query search result as a tsv file format')

    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '-s',
        '--source',
        help='source file path',
        required=True,
    )
    required.add_argument(
        '-d',
        '--destination',
        help='destination directory path to save output file as tsv format',
        required=True,
    )

    return parser.parse_args(args)


def main():
    # args = _parse_args()

    # if not os.access(args.destination, os.W_OK):
    #     msg = 'Cannot write to destination: {}'.format(args.destination)
    #     sys.exit(msg)
    #
    # if os.getenv('AMAZON_ACCESS_KEY') is None:
    #     msg = 'AMAZON_ACCESS_KEY should be set as a environment variable'
    #     sys.exit(msg)
    # if os.getenv('AMAZON_SECRET_KEY') is None:
    #     msg = 'AMAZON_SECRET_KEY should be set as a environment variable'
    #     sys.exit(msg)
    # if os.getenv('AMAZON_ASSOC_KEY') is None:
    #     msg = 'AMAZON_ASSOC_KEY should be set as a environment variable'
    #     sys.exit(msg)
    # if not os.path.isfile(args.source):
    #     msg = 'Source should be a file'
    #     sys.exit(msg)
    #
    # (filename, ext) = os.path.splitext(args.source)
    # if ext != '.tsv':
    #     print(os.path.splitext(args.source))
    #     msg = 'Source should be tsv file format'
    #     sys.exit(msg)
    # if not os.path.isdir(args.destination):
    #     msg = 'Destination should be a directory'
    #     sys.exit(msg)



    # book_status = BookQuery()
    # output_path = book_status.generate_output(
    #     args.source,
    #     args.destination
    # )

    # print(output_path)

    book_status = BookQuery()
    output_path = book_status.generate_output(
        "E:\Work\Real-Work\Wayback Machine\AmazonBookQuery_12_12_07_34\source_files\Amazontestquery.tsv",
        "E:\Work\Real-Work\Wayback Machine\AmazonBookQuery_12_12_07_34\source_files"
    )


if __name__ == '__main__':
    main()