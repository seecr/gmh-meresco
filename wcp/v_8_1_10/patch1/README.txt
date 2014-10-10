This patch adds an extra column to the harvester Validatie Errors table with the description of the Validation Error itself.
Tested on: Meresco Harvester (8.1.10).

Add two new files to: /usr/lib/python2.6/site-packages/meresco/harvester/controlpanel/html/dynamic
- invalid_gmh.sf
- invalidRecord_gmh.sf
scp wilkos@gharvester21.dans.knaw.nl:/home/wilkos/gmh/wcp_patch/invalid*.sf .

Create a backup of the following two files, before overwritting/applying the patched onces:
cp /usr/lib/python2.6/site-packages/meresco/harvester/controlpanel/slowfoottemplates/invalid /usr/lib/python2.6/site-packages/meresco/harvester/controlpanel/slowfoottemplates/invalid_bckp
cp /usr/lib/python2.6/site-packages/meresco/harvester/controlpanel/slowfoottemplates/showHarvesterStatus /usr/lib/python2.6/site-packages/meresco/harvester/controlpanel/slowfoottemplates/showHarvesterStatus_bckp

Then update/overwrite two existing files in/from: /usr/lib/python2.6/site-packages/meresco/harvester/controlpanel/slowfoottemplates
scp wilkos@gharvester21.dans.knaw.nl:/home/wilkos/gmh/wcp_patch/invalid .
scp wilkos@gharvester21.dans.knaw.nl:/home/wilkos/gmh/wcp_patch/showHarvesterStatus .
