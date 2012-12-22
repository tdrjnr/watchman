#!/usr/bin/python
from __future__ import print_function
import sys
import os
import re
import commands
import datetime

# Global variables
searches = {} # dictionary to store all searches found in the conf
log = open( "/var/log/watchman_log", "a" ) # Lets try and open a log in /var/log to write to
pwd = os.path.dirname( os.path.realpath( __file__ ) ) # I'm running from here


# Check for a config file and load the contents
def loadConfig():
    try:
        f = open( pwd + "/watchman.conf", "r" )

    except IOError, e:
        rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
        print( rightNow + " - I could not find watchman.conf in the working directory (" + pwd + "). Error: %s" % e, file=log )

        try:
            f = open( pwd + "/watchman.conf", "w" )
            print( "[What are you searching for?]\n#You can add multiple search patterns in the key=value formation e.g.\n#Search1=searchd\n#Search2=searche", file=f )

            rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
            print( rightNow + " - It's ok.  I created a blank for you but you'll need to configure it or there's nothing for me to do!", file=log )

            f = open( pwd + "/watchman.conf", "r" )

        except IOError, e:
            rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
            print( rightNow + " - I tried to create a blank template for you but unfortunately I couldn't.  You're on your own muchacho." )
            print( rightNow + " - Error was: %s " % e, file=log )

    for line in f:
        # Skipping the rubbish
        if re.search( "^\[", line ):
            continue # Lets ignore section headers. the conf isn't complicated enough yet...
        if re.search( "^#", line ):
            continue # Lets ignore comments of course
        if line == '\n':
            continue # We don't care about blank lines do we?

        # Reading in the useful info
        matches = re.search( "^(Search\d+)=(.+)", line )

        if matches:
            # We want the search name and the search string.
            searches[matches.group(1)] = matches.group(2)

    return searches


# Run the searches
def runSearches():
    if searches:
        # Log readability separator
        rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
        print( "\n############### Search starting - %s ###############" % rightNow, file=log )

        for search, pattern in searches.iteritems():
            rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
            print( "%s - Running %s...\n%s - Searching for \"%s\"..." % ( rightNow, search, rightNow, pattern ), file=log )

            commOutput = commands.getstatusoutput( "pgrep -fl \"" + pattern + "\"" )

            # Bummer... The pgrep is in the list of search results causing false positives.  Need to RE them out.
            # I've tried ps and considered querying /proc using glob but they all require as much work as the grep.
            # Most Python resources recommend avoiding RE where possible (hog) but given the size of the project
            # and since I like using RE I'm going to proceed with that.

            commOutputList = commOutput[1].split( '\n' )

            for item in commOutputList:
                if re.search( "^.+pgrep.+", item ):
                    commOutputList.remove( item )

            if commOutputList:
                rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
                print( rightNow + " - %s is currently running.  Nothing to do!\n" % pattern, file=log )
            else:
                rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
                print( rightNow + " - Oh dear! Restarting %s\n" % pattern, file=log )

                restartProcess( pattern )

    else:
        rightNow = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
        print( rightNow + " - There were no searches in the config (" + pwd + "/watchman.conf).", file=log )
        sys.exit()


# Function to restart a process from a failed search
def restartProcess( search ):
    pass

# Run the script
loadConfig()

runSearches()