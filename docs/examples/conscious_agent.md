# Conscious Agent

The **Conscious Agent** is a basic multi-agent system that is called from the [conscious_assistant.py](../../apps/conscious_assistant/conscious_assistant.py) Flask app. 

**Note**: Running the flask app will continuously call the agents and can rack up on your token consumption.
**Note**: The flask app will store memory items in a file locally. You can turn this feature off by changing the flag in [list_topics.py](../../coded_tools/kwik_agents/list_topics.py)
---

## File

[conscious_agent.hocon](../../registries/conscious_agent.hocon)

---

## Description

Once you run the [conscious_assistant.py](../../apps/conscious_assistant/conscious_assistant.py) Flask app, it will provide you with a link, which you can open in your browser to play around with the conscious assistant. This assistant is running constantly in the background and "thinking". It may even initiated a dialog. When you chat with it, it will remember facts about what you said, and store them in memory, which is saved in a local file.

The hocon file includes an example of calling a coded_tool in a non-default path. This is for the memory operations, for which the kwik_agents coded tools are reused here.

---

