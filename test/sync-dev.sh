#!/usr/bin/env ncs_cli

request devices device sim* sync-from
config
request devices device sim* delete-config
request devices device sim* sync-to
set devices device sim* config ios:tailfned police cirmode
commit
exit
show devices brief
