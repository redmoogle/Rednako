# Data Folder

This is where stuff like 'guild_{}' thing goes, these contain json encoded data for each guild

As of now you will see `guild_economy.json`, `guild_settings.json`, `guild_muted.json` and `guild_xp.json`

economy stores a dictonary for each server containing something like this

```
"GUILDID": {
    "MEMBERID": MONEY,
    "MEMBERID2": MONEY
}
```

settings store general guild settings

```
"GUILDID": {
    "DJMODE": null,
    "PREFIX": "=",
    "ERRORS": false
}
```

muted store mutes

```
"GUILDID": {
    "ROLE": ID
    MEMBERID: {
    "EXPERATION": 0
    }
}
```

finally, xp stores XP for people
```
"GUILDID": {
    "ENABLED": false,
    MEMBERID: {
      "XP": XP,
      "LAST_USED": 0,
      "GOAL": 20
      "LEVEL": 0
    }
}
```
