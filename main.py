import csv
import json

import colorama
from clubhouse.clubhouse import Clubhouse
from pick import pick

colorama.init()


class FollowersIDScraper:
    def __init__(self):
        self.clubhouse = Clubhouse()

    def login(self):
        phone_num = input('Enter your phone number (for example +1 2345): ')
        self.clubhouse.start_phone_number_auth(phone_num)  # Send the verification code
        verification_code = input('Enter the code you received: ')
        authorization_json = self.clubhouse.complete_phone_number_auth(phone_num, verification_code)
        # Login with the received code
        user_id = str(authorization_json['user_profile']['user_id'])  # Get the logged in user's user id
        user_token = str(authorization_json['auth_token'])  # Get the authorization token
        self.clubhouse.__init__(user_id, user_token)  # Set the values in the Clubhouse object

    def get_followers(self, account_id):
        page_num = 1
        followers_id = []

        while True:
            followers = self.clubhouse.get_followers(account_id, page=page_num)
            # Use the get_followers endpoint (the response is a json parsed to a dict object)
            for follower in followers['users']:
                followers_id.append(follower['user_id'])  # Add the follower's id to the list

            page_num = followers['next']  # Get the 'next' parameter from the response
            # (represents the next page that can be queried)
            if not page_num:  # If it's the last page, stop the loop
                break

        return followers_id

    def get_user_id(self, username):
        users = self.clubhouse.search_users(username)  # Search for a username
        if 'users' not in users:
            return None

        users = users['users']  # Get the list of results
        for user in users:
            if user['username'] == username:  # If the needed username is the same as the result, return the user's id
                return user['user_id']

    def scrape_followers(self, username, csv_filename='output.csv', json_filename='output.json'):
        account_id = self.get_user_id(username)  # Get the user id of the needed account
        if not account_id:
            print('The username is not found. Please try again')
            return
        followers = self.get_followers(account_id)  # Get the list of followers
        with open(csv_filename, 'a+', newline='') as csv_file:  # Open the csv file
            writer = csv.writer(csv_file)
            for follower in followers:
                writer.writerow([follower])  # Write the follower's id
        print(f'Finished adding followers to {csv_filename}')

        with open(json_filename, 'a+') as json_file:  # Open the csv file
            json.dump(followers, json_file, indent=4, sort_keys=True)  # Write the json to the file
        print(f'Finished adding followers to {json_filename}')


class UsernameChecker:
    def __init__(self):
        self.clubhouse = Clubhouse()

    def login(self):
        phone_num = input('Enter your phone number (for example +1 2345): ')
        self.clubhouse.start_phone_number_auth(phone_num)
        verification_code = input('Enter the code you received: ')
        authorization_json = self.clubhouse.complete_phone_number_auth(phone_num, verification_code)
        user_id = str(authorization_json['user_profile']['user_id'])
        user_token = str(authorization_json['auth_token'])
        self.clubhouse.__init__(user_id, user_token)

    def is_user_taken(self, username):
        users = self.clubhouse.search_users(username)
        if 'users' not in users:
            return False

        users = users['users']
        for user in users:
            if user['username'] == username:
                return True
        return False
        # return any(user['username'] == username for user in users)

    def check_usernames_existence(self, usernames: list = None, username_file: str = None,
                                  output_file: str = 'available_users.txt'):
        if username_file:
            with open(username_file) as usernames:
                with open(output_file, 'a+') as output:
                    for username in usernames:
                        if not self.is_user_taken(username.strip()):
                            print(f'{colorama.Fore.GREEN}User {username} does not exists!')
                            output.write(username)
        else:
            with open(output_file, 'a+') as output:
                for username in usernames:
                    if not self.is_user_taken(username.strip()):
                        print(f'{colorama.Fore.GREEN}User {username} does not exists!')
                        output.write(username)


if __name__ == '__main__':
    title = 'Please choose what you want to do: '
    options = ['Get a user followers', 'Check existing usernames']
    option, index = pick(options, title)

    if index == 0:
        follower_scraper = FollowersIDScraper()
        follower_scraper.login()
        searched_user_id = input('Enter the username to scrape for followers: ')
        follower_scraper.scrape_followers(searched_user_id)

    else:
        user_checker = UsernameChecker()
        user_checker.login()
        users_filename = input('Enter the filename with usernames: ')
        user_checker.check_usernames_existence(username_file=users_filename)
