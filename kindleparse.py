#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-14 14:29:25
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import asyncio
import json
import os
import re

from motor import motor_asyncio


class KindleCommentParser:

    def __init__(self):
        __client = motor_asyncio.AsyncIOMotorClient("mongodb://admin:password@pvgd56578494a")
        __db = __client.test_db
        self.__collection = __db.test_collection

    async def parse_txt(self):
        with open("My Clippings.txt", encoding='utf-8') as f:
            lines = f.readlines()
        result = []
        self._parser(lines, result)
        comments = await self._parser_to_json(result)
        
    def _parser(self, documents, output_list):
        sub_doc = []
        for doc in documents:
            sub_doc.append(doc.strip('\n'))
            if doc.startswith('==='):
                output_list.append(sub_doc)
                sub_doc = []
                continue

    async def _parser_to_json(self, input_doc):
        if not isinstance(input_doc, list):
            raise ValueError("should be list")
        output_list = []
        for doc in input_doc:
            comment_json = {}
            title, location_time, _, comment, _ = doc
            comment_json['title'] = title
            comment_json['location'] = self.convert_location(location_time)
            comment_json['type'] = location_time.split('|')[0][-3:]
            comment_json['timestamp'] = location_time.split('|')[1]
            comment_json['comment'] = comment
            output_list.append(comment_json)
            await self.save_to_mongo(comment_json)
        return output_list

    @classmethod
    def convert_location(cls, location):
        location = location.split('|')[0]
        res = re.findall('#\d.+\d+', location)
        if len(res) == 0:
            return None
        return res[0]


    async def save_to_mongo(self, document):
        exists = await self.__collection.find_one(document)
        if not exists:
            result = await self.__collection.insert_one(document)
        else:
            print(document)

if __name__ == '__main__':
    parser = KindleCommentParser()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser.parse_txt())

