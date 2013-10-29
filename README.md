cf-buildpack-wiki
================================================================================

A CloudFoundry buildpack to deploy <https://github.com/WardCunningham/wiki>


usage
--------------------------------------------------------------------------------

* create a new empty directory, and cd into it:

        mkdir wiki-sample
        cd wiki-sample

* create a `config.json` file in that directory.  There should be one entry, for
  the eventual hosted url of your server.  In this case, given the answers
  to the questions we answer below, the hosted url will be
  `bob-sample-wiki.example.com`.  You will need to use either 
  https or http as appropriate, in the url.  Eg:

        {
            "url": "https://bob-sample-wiki.example.com"
        } 
        

* push with the buildpack:

        cf push --buildpack https://github.com/pmuellr/cf-buildpack-wiki.git

* when prompted for `Name>`, enter a unique host name:

        Name> bob-sample-wiki

* when prompted for `Instances>`, `Memory Limit>`, `Subdomain>`, and `Domain>`, 
  you can use the defaults

        Instances> 1
        
        1: 128M
        2: 256M
        3: 512M
        4: 1G
        Memory Limit> 256M
        
        Creating bob-sample-wiki... OK
        
        1: bob-sample-wiki
        2: none
        Subdomain> bob-sample-wiki
        
        1: example.com
        2: none
        Domain> example.com
        
        Creating route bob-sample-wiki.example.com... OK
        Binding bob-sample-wiki.example.com to bob-sample-wiki... OK  
        
* when prompted for `Create services for application?>`, answer `y`:

        Create services for application?> y

* when prompted for `What kind?`, pick a mongo database:

        ...
        4: mongodb 2.2
        5: mysql 5.5
        6: postgresql 9.1
        7: rabbitmq 2.8
        8: redis 2.6
        ...
        What kind?> 4

* when prompted for `Name?`, use the default:

        Name?> mongodb-12c45


* when prompted for `Which plan?`, use the default:

        1: 100: Dedicated server, shared VM, 250MB storage, 10 connections
        Which plan?> 1

* the service is created:

        Creating service mongodb-12c45... OK
        Binding mongodb-12c45 to bob-sample-wiki... OK

* when prompted for `Create another service?>`, answer the default, `n`:

        Create another service?> n

* when prompted for `Bind other services to application?>`, answer the default, `n`:

        Bind other services to application?> n

* when prompted for `Save configuration?>`, answer `y`, which will create a
  manifest.yml file in the current directory:

        Save configuration?> y

* staging begins - take about a minute

        Saving to manifest.yml... OK
        Uploading bob-sample-wiki... OK
        Preparing to start bob-sample-wiki... OK
        -----> Downloaded app package (4.0K)
        Initialized empty Git repository in /tmp/buildpacks/.git/.git/
        running python /tmp/buildpacks/.git/bin/compile.py /tmp/staged/app /tmp/cache
        Initialized empty Git repository in /tmp/staged/app/wiki/.git/
        npm http GET https://registry.npmjs.org/wiki-client
        npm http GET https://registry.npmjs.org/flates/0.0.5
        ...

* staging done, droplet uploaded and app started:

        ...
        compile.py: build time: 105.5 seconds
        -----> Uploading droplet (19M)
        Checking status of app 'bob-sample-wiki'...
          1 of 1 instances running (1 running)
        Push successful! App 'bob-sample-wiki' available at http://bob-sample-wiki.example.com

* browse your new wiki!


why
--------------------------------------------------------------------------------

Server developers may want to make a *canned* version of their server available
with the simplest possible deployment.  Rather than require the user to locally
install their server, they can have the buildpack do all the work.

This model can be extended by taking into account files in the current directory.
For example, with [wiki](https://github.com/WardCunningham/wiki)
you could imagine populating the [plugins directory](https://github.com/WardCunningham/wiki/tree/master/client/plugins)
with your own set of plugins.  Go crazy.
