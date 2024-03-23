""" Transfer teams and members from one GitHub organization to another """
import os
import argparse
import requests

# Retrieving GitHub access token from environment variable
access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
if not access_token:
    print("Error: GitHub access token not found. Please set GITHUB_ACCESS_TOKEN environmental variable.")

# Parsing command-line arguments
parser = argparse.ArgumentParser(description="Transfer teams and members from one GitHub organization to another.")
parser.add_argument("--source_org", help="Name of the source organization")
parser.add_argument("--destination_org", help="Name of the destination organization")
args = parser.parse_args()

# Access parsed arguments 
source_organization = args.source_org
destination_organization = args.destination_org

# This variable stores the URL for the GitHub API
apiUrl = "https://api.github.com"

def get_teams(source_org, access_token):
    """
    Retrieve teams from a GitHub organization.

    Args:
        source_org (str): Name of the source organization.
        access_token (str): GitHub access token for authentication.

    Returns:
        dict or None: A dictionary containing information about the teams retrieved from the source organization.
                      Returns None if the request fails.
    """
    url = f"{apiUrl}/orgs/{source_org}/teams"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch teams from {source_org}. Status code: {response.status_code}")
        return None

def get_team_members(team_id, access_token):
    """
    Retrieve members of a GitHub team.

    Args:
        team_id (int): The ID of the GitHub team.
        access_token (str): GitHub access token for authentication.

    Returns:
        dict or None: A dictionary containing information about the members of the team.
                      Returns None if the request fails.

    """
    url = f"{apiUrl}/teams/{team_id}/members"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch members for team {team_id}. Status code: {response.status_code}")
        return None

def create_team(destination_org, access_token, team_data):
    """
    Create a team in a GitHub organization.

    Args:
        destination_org (str): The name of the destination GitHub organization.
        access_token (str): GitHub access token for authentication.
        team_data (dict): A dictionary containing data for creating the team.

    Returns:
        dict or None: The JSON response containing information about the created team if successful, otherwise None.    """
    url = f"{apiUrl}/orgs/{destination_org}/teams"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, json=team_data, headers=headers)

    if response.status_code == 201:
        print(f"Team - {team_data['name']} created successfully in {destination_org}")
        return response.json()   # Return the JSON response containing information about the created team
    else:
        print(f"Failed to create team {team_data['name']} in {destination_org}. Status code: {response.status_code}")
        return None

def add_members_to_team(team_id, access_token, members):
    """
    Add members to a GitHub team.

    Args:
        team_id (int): The ID of the GitHub team to which members will be added.
        access_token (str): GitHub access token for authentication.
        members (list): A list of dictionaries, where each dictionary contains information
                        about a member to be added. Each dictionary should contain at least
                        the 'login' key with the GitHub username of the member.
    """
    if not team_id:
        print("Team ID is not valid. Skipping adding members.")
        return
    
    url = f"{apiUrl}/teams/{team_id}/memberships"
    headers = {"Authorization": f"Bearer {access_token}"}
    for member in members:
        username = member['login']
        response = requests.put(f"{url}/{username}", headers=headers)

        if response.status_code == 200:
            print(f"Member - {username} added successfully to team {team_id}")
        else:
            print(f"Failed to add member {username} to team {team_id}. Status code: {response.status_code}")

def transfer_teams(source_org, destination_org, access_token):
    """
    Transfer teams from one GitHub organization to another.

    Args:
        source_org (str): The name of the source GitHub organization.
        destination_org (str): The name of the destination GitHub organization.
        access_token (str): GitHub access token for authentication.
        """
    # Get teams from source organization
    teams = get_teams(source_org, access_token)
    if teams:
        for team in teams:
            # Create team in destination organization
            new_team_response = create_team(destination_org, access_token, team)
            if new_team_response:
                new_team_id = new_team_response['id']
                # Fetch members of the source team
                team_members = get_team_members(team['id'], access_token)
                if team_members:
                    # Add members to the destination team
                    add_members_to_team(new_team_id, access_token, team_members)

transfer_teams(source_organization, destination_organization, access_token)
