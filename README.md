The Boston Marathon
======

# Data

It's recommended you first create and activate a virtualenv with:

    virtualenv virt
    source virt/bin/activate

Whether or not you use virtualenv:

    pip install -r requirements.txt

To search the results and collect the urls for each individual runner, run:

    ./scripts/crawl.py crawl
    
This will crawl about 1,075 pages and cache the HTML pages in the ```cache``` directory.
It will also create a file called ```all_runners.json``` in the ```data``` directory. Then run:

    ./scripts/crawl.py times