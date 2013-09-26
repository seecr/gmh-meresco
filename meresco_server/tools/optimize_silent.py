## begin license ##
#
#    Meresco Tools can help administrator or developers for Meresco
#    based tasks.
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
#
#    This file is part of Meresco Tools.
#
#    Meresco Tools is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Tools is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Tools; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from sys import argv, path
from glob import glob
from os import remove
from os.path import join

from meresco.components.facetindex.merescolucene import IndexWriter, merescoStandardAnalyzer
from meresco.tools.lucenetools import unlock

def removeTrackerFiles(path):
    for filename in glob(join(path, '*.deleted')) + \
                glob(join(path, '*.docids')) + \
                glob(join(path, 'tracker.segments')):
        remove(filename)


def optimize(args):

    path = '/data/meresco/index'
    print "You are about to optimize the index at '%s'." % path
    print "This process can take a few minutes to complete, depending"
    print "on the size of your index."
    print "BEWARE: do not have another process reading or writing this directory.\n"
#    raw_input("Press any key to continue (Ctrl-C to break) ")
    unlock(path)
    print 'Optimizing index', path
    writer = IndexWriter(path, merescoStandardAnalyzer, False)
    writer.optimize()
    writer.close()
    print 'Removing tracker files'
    removeTrackerFiles(path)
    print 'Finished'


if __name__ == '__main__':
    optimize(argv)