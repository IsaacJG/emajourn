# Emajourn
Email to [Day One](http://dayoneapp.com/)

### What it is
Emajourn takes emails from a specific folder, and converts them into DayOne journal entries.
It is essentially a Python version of [email-to-DayOne](https://github.com/nicatronTg/email-to-DayOne) by nicatronTg, though this lacks some of the features he includes. This is because Emajourn uses the [DayOne CLI](http://dayoneapp.com/tools/cli-man/) utility, and email-to-DayOne uses a Ruby gem that interacts directly with the DayOne journal files.

### Features

* Journal time stamping
* Images (can only use one image per journal entry)

### Installation

1. Clone this repo: `git clone https://github.com/isaacJG/emajourn.git`
2. Copy config.example.json to config.json and customize it
	1. imap_server - the server you want to get your email off of (example: `imap.googlemail.com`
	2. imap_username - your username (email address)
	3. imap_password - your email password
	4. imap_port - you shouldn't have to change this (993 by default), unless you aren't using SSL
	5. use_ssl - whether or not to use SSL
	6. folder - the folder to retreive emails from (**Note: emajourn permanently deletes emails after processing, it is recommended to have a dedicated journal folder, not just your inbox**)
	7. processing_count - the maximum number of emails to process per run
	8. images_folder - the folder (relative path) to temporarily store images downloaded from emails
3. Run emajourn: `python3 emajourn.py`

It is recommended to use some sort of automation program with this, so that you can automatically run Emajourn every set period of time. One option is to set it to run on login, unless you want the emails to be processed quickly after arrival.

### Warning
Emajourn will permanently delete emails from the set folder after processing them! (You can disable this by passing `--no-delete` in the command line, but that flag is only for testing, because it will cause duplicate entries to be made in DayOne)  
I am not responsible for any damage this may cause to your DayOne journal, you are using this program at your own risk. Keep in mind I am using the CLI tool provided by DayOne, so the only risks involved in using Emajourn are those inherited from that utility.

### License
GPL v3.0

### Contributions
I do not have DayOne, so this was written somewhat blindly. I know many improvements could be made, especially if there were a python module that can directly interact with DayOne journal entries. Feel free to make pull requests and create issues!