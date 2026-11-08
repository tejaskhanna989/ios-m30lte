#!/usr/bin/env perl
#
# Minimal availability.pl for M30LTE XNU build
# Provides iOS and macOS version lists for _symbol_aliasing.h generation
#

use strict;
use warnings;

my $platform = shift @ARGV || '';

if ($platform eq '--ios') {
    # iOS versions for M30LTE (iOS 16/17/18 era)
    print "16.0\n";
    print "16.1\n";
    print "16.2\n";
    print "16.3\n";
    print "16.4\n";
    print "16.5\n";
    print "16.6\n";
    print "17.0\n";
    print "17.1\n";
    print "17.2\n";
    print "17.3\n";
    print "17.4\n";
    print "17.5\n";
    print "18.0\n";
} elsif ($platform eq '--macosx') {
    # macOS versions
    print "13.0\n";
    print "13.1\n";
    print "13.2\n";
    print "13.3\n";
    print "13.4\n";
    print "13.5\n";
    print "13.6\n";
    print "14.0\n";
    print "14.1\n";
    print "14.2\n";
    print "14.3\n";
    print "14.4\n";
    print "14.5\n";
    print "15.0\n";
} else {
    # Default: print both
    print "16.0\n16.1\n16.2\n16.3\n16.4\n16.5\n16.6\n17.0\n17.1\n17.2\n17.3\n17.4\n17.5\n18.0\n";
    print "13.0\n13.1\n13.2\n13.3\n13.4\n13.5\n13.6\n14.0\n14.1\n14.2\n14.3\n14.4\n14.5\n15.0\n";
}

exit 0;