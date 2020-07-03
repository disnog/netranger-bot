#!/usr/bin/env python3

#  network_ranger - db.py
#  Copyright (C) 2020  Jason R. Rokeach
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pymongo import MongoClient
from pymongo import UpdateOne
from pymongo import ReturnDocument
import json


class Db:
    def __init__(
        self,
        host="localhost",
        port=27017,
        mongo_user=None,
        mongo_pass=None,
        dbname="network_ranger",
    ):
        self.client = MongoClient(
            host=host, port=port, username=mongo_user, password=mongo_pass
        )
        self.db = self.client[dbname]
        if dbname not in self.client.list_database_names():
            print(f'Database named "{dbname}" does not exist; initializing.')
        self.users = self.db.users
        self.config = self.db.config

    def add_existing_members(self, guild):
        members = guild.members
        op_list = []
        for member in members:
            if member.bot:
                # Do not add bots to the DB.
                continue
            permanent_roles = []
            for role in member.roles:
                if role.name == "Members" or role.name == "Member":
                    permanent_roles.append("Member")
                elif role.name == "!eggs":
                    permanent_roles.append("!eggs")
            m = {
                "_id": member.id,
                "name": member.name,
                "nick": member.nick,
                "discriminator": member.discriminator,
                "permanent_roles": permanent_roles,
            }

            op_list.append(UpdateOne({"_id": m["_id"]}, {"$set": m}, upsert=True))
        self.users.bulk_write(op_list)
        self.add_first_joined_ats(guild)
        self.add_member_numbers()

    def add_first_joined_ats(self, guild):
        """Member is a discord members object"""
        for user in self.users.find({"first_joined_at": None}):
            member = guild.get_member(user["_id"])
            if member:
                self.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"first_joined_at": member.joined_at.timestamp()}},
                )

    def add_member_numbers(self):
        sorted_users = self.users.find(
            {
                "member_number": None,
                "first_joined_at": {"$gt": 0},
                "permanent_roles": "Member",
            }
        ).sort("first_joined_at")
        for user in sorted_users:
            # Get the next number to assign
            nextnumber = self.config.find_one_and_update(
                {"name": "last_member_number"},
                {"$inc": {"value": 1}},
                projection={"value": True, "_id": False},
                return_document=ReturnDocument.AFTER,
                upsert=True,
            )["value"]
            # Update the user
            self.users.update_one(
                {"_id": user["_id"]}, {"$set": {"member_number": nextnumber}}
            )

    def add_member(self, member):
        m = {
            "_id": member.id,
            "name": member.name,
            "nick": member.nick,
            "discriminator": member.discriminator,
            "permanent_roles": [],
        }
        self.users.insert_one(m)

    def add_permanent_role(self, member_id, role_name):
        self.users.update_one(
            {"_id": member_id}, {"$push": {"permanent_roles": role_name}}
        )

    def get_member_number(self, member_id):
        return self.users.find_one({"_id": member_id})["member_number"]

    def get_permanent_roles(self, member_id):
        permanent_roles = list()
        try:
            permanent_roles.extend(
                self.users.find_one({"_id": member_id})["permanent_roles"]
            )
        except TypeError:
            pass
        return permanent_roles
