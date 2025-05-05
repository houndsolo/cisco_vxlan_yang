#!/usr/bin/env python3

from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit

def global_lock(task):
    lock = task.run(netconf_lock, datastore="candidate", operation="lock")
    task.host["manager"] = lock.result.manager

def global_unlock(task):
    task.run(netconf_lock, datastore="candidate", operation="unlock", manager=task.host["manager"])
