# Data Folder

This is where stuff like 'guild_{}' thing goes, these contain json encoded data for each guild

As of now you will see `guild_economy.json`, `guild_prefix.json` and `guild_djmode.json`

economy stores a dictonary for each server containing something like this

```
"GUILDID": {
"MEMBERID": MONEY,
"MEMBERID2": MONEY
}
```

prefix stores the prefix of that guild

```
"GUILDID": "=="
```

and finally, djmode stores a role to check for (doesn't check if set to None/null)
```
"GUILDID": null,
"GUILDID": 788875356722954320
```

Along with that the database is stored in there which contains two tables: `mutes` and `longmutes` both are encoded with the fields: `id(INT), experation(TIME), guild(INT), role(INT)`

ID is the int ID of the user that was muted
Experation is the time at which it will expire and be removed
Guild is the int of the guild they were muted in
Role is the int of the role that was applied
