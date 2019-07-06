Renames files in mass using regular expressions. Written in Python 3


# Help Text
```
rename <options> file_one file_two ...
renames files based on python regular expressions

options:
    -h --help    prints help text then exits.
    -v --verbose prints more verbose messages. a really long description that
               should be wrapped.
  -d --dryrun  prints what renames would happen without doing them.
  -f --filter= only works with files that match this regex.
  -r --result= only performs renames that result in a file that matches this
               regex.
  -a --action= add an action to be performed on file names. actions are done in
               the order they are specified. (see actions)

Actions:
  d:regex          | removes all occurances of regex.
  r:regex1:regex2  | replaces all occurances of regex1 with regex2.

Example:
Files:
   'dexter episode 1 [random crap].mp4'
   'dexter episode 2 [random crap].mp4'
   'dexter episode 3 [random crap].mp4'
   'other show episode 1.mp4'

rename -f 'dexter episode [0-9] \[.*\].mp4' -r 'Dexter E[0-9].mp4' -a 'r:dexter episode ([0-9]) .*:Dexter E\1.mp4' *

Renamed files:
   'Dexter E1.mp4'
   'Dexter E2.mp4'
   'Dexter E3.mp4'
```


# Example
### Given the following files:
```
  ./"series_name episode 1 [hello world] first_ep_title.mp4"
  ...
  ./"series_name episode 34 [hello world] thirty_fourth_ep_title.mp4"
```

```
rename -f 'series_name episode.*' -r 'Series Name.*\.mp4' -a 'r:series_name:Series Name' *
```

### Files:
```
  ./"Series Name episode 1 [hello world] first_ep_title.mp4"
  ...
  ./"Series Name episode 34 [hello world] thirty_fourth_ep_title.mp4"
```

```
-f only files matching the following regex will be renamed
-r files can only be renamed to something matching this regex
-a an action to do on all the file names. In this case it is replacing series_name with Series Name.
```

### Todo:
  * Add image taken date keyword.

