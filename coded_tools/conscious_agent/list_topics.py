import json
import logging
import os
from typing import Any
from typing import Dict

from neuro_san.interfaces.coded_tool import CodedTool

LONG_TERM_MEMORY_FILE = True  # Store and read memory from file
MEMORY_FILE_PATH = "./"
MEMORY_DATA_STRUCTURE = "TopicMemory"


class ListTopics(CodedTool):
    """
    CodedTool implementation which provides a way to replace the instructions of an agent in an agent network in sly
    """

    def __init__(self):
        self.topic_memory = None

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent.  This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "app_name" the name of the One Cognizant app for which the URL is needed.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    None

        :return:
            In case of successful execution:
                The full agent network as a string.
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """
        self.topic_memory = sly_data.get(MEMORY_DATA_STRUCTURE, None)
        if not self.topic_memory:
            if LONG_TERM_MEMORY_FILE:
                self.read_memory_from_file()
            else:
                return "NO TOPICS YET!"

        logger = logging.getLogger(self.__class__.__name__)
        logger.info(">>>>>>>>>>>>>>>>>>>ListTopics>>>>>>>>>>>>>>>>>>")
        topics_str = self.get_memory_topics()
        logger.info("The resulting list of topics: \n %s", str(topics_str))
        sly_data[MEMORY_DATA_STRUCTURE] = self.topic_memory
        logger.info(">>>>>>>>>>>>>>>>>>>DONE !!!>>>>>>>>>>>>>>>>>>")
        return topics_str

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)

    def read_memory_from_file(self):
        """
        Reads the topic memory dictionary from a JSON file if it exists.
        Otherwise initializes an empty dictionary.
        """
        file_path = MEMORY_FILE_PATH + MEMORY_DATA_STRUCTURE + ".json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.topic_memory = json.loads(content) if content else {}
        else:
            self.topic_memory = {}

    def get_memory_topics(self) -> str:
        """
        Retrieves the full list of memory topics.

        Returns:
        - list: A sorted list of all memory topics.
        """
        return str(sorted(list(self.topic_memory.keys())))
