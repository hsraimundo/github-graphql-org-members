import sys
import json
import requests

# expecting arguments for authorization [1]
github_bearer_token = sys.argv[1]
github_organization = sys.argv[2]

# read configuration file
with open('config.json', 'r') as configFile:
    config = json.load(configFile)

    page_size = config["github"]["graphql"]["pagesize"]
    url = config["github"]["graphql"]["url"]

# query format for getting the github user names and sky email linked via sso
query_format = \
        ("{{\n"
         "  organization(login: \"{org}\") {{\n"
         "    samlIdentityProvider {{\n"
         "      ssoUrl\n"
         "      externalIdentities(first: {page_size!r} {filter}) {{\n"
         "        edges {{\n"
         "          cursor\n"
         "          node {{\n"
         "            guid\n"
         "            samlIdentity {{\n"
         "              nameId\n"
         "            }}\n"
         "            user {{\n"
         "              login\n"
         "            }}\n"
         "          }}\n"
         "        }}\n"
         "      }}\n"
         "    }}\n"
         "  }}\n"
         "}}\n")


# A simple function to use requests.post to make the API call. Note the json= section.
def run_query(url, query_format, headers, page_size, cursor=None):
    if cursor is None:
        cursor = "null"
    query = query_format.format(org=github_organization, page_size=page_size, filter=", after: " + cursor + "")
    request = requests.post(url, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# prepare the auth header for github
headers = {
    "Authorization" : "Bearer " + github_bearer_token
}


next_cursor = None

# Iterate over the users in github and output to output.csv
with open("output.csv", 'w') as output:
    output.truncate(0)

    iteration = 0

    try:
        while True:
            print("Iteration: " + repr(iteration))
            iteration += 1;

            result = run_query(url, query_format, headers, page_size, next_cursor)
            result = result["data"]["organization"]["samlIdentityProvider"]["externalIdentities"]["edges"]

            for tuple in result:
                try:
                    sky_email = tuple["node"]["samlIdentity"]["nameId"]
                except:
                    sky_email = ""

                try:
                    github_login = tuple["node"]["user"]["login"]
                except:
                    github_login = ""

                outputs = sky_email + ", " + github_login + "\n"
                output.writelines(outputs)
                print(outputs)

            if next_cursor == tuple["cursor"]:
                break
            next_cursor = "\"" + tuple["cursor"] + "\""
            output.flush()
    except:
        output.flush()