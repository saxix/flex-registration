from threading import local

state = local()
state.collect_messages = False
