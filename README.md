# ddt-helper
Helper Discord bot to mass assign group roles from a .csv file input

# Usage:

`$assigngroups`:
- Requires one .csv file attached to the invocation message
- The .csv file expected is one where the first row of the spreadsheet contains the group names, with each group's names in columns underneath (You can create .csv files from Google Spreadsheets via `File` -> `Download` -> `Comma Separated Values (.csv)`):

Group 1 | Group 2 | Group 3
--------|---------|---------
 A#0000 | B#7890  | C#1100
 D#1234 | E#5000  | F#8000
- Channel links may be added after `$assigngroups` to have the bot send out group assignments to the specified channel(s), e.g. `$assigngroups #admin-office`. Note that the channel links must be the interactive kind (blue in color).

`$removegroups`:
- Strips "Group" roles from all users. This command should be used after a tourney has concluded.
