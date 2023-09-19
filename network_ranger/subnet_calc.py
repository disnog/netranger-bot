import ipcalc
import re


# Checks args list and chooses which function to use depending on single or multiple inputs
def subnet_calc_function():

    # composing a general error message to return if anything goes wrong
    error_message = (
        "Invalid input."
        "\nUse syntax: "
        "\n-ipcalc info 10.10.10.2/23"
        "\nor"
        "\n-ipcalc info 2001:db8:2001::10/64"
    )

    # First check if there is one or multiple args (CIDR or full_mask).
    # Both alternatives start with creating an object.
    # If there's an value error of some sort, then the exception will return an error message

    try:
        if len(argumentList) == 1:
            # IPv4 or IPv6 address with CIDR

            subnet_1 = ipcalc.Network(argumentList[0])

            # Creating IPv4 message
            if subnet_1.version() == 4:
                if re.match(RP_FULLCIDRv4, argumentList[0]):
                    message = (
                        f"Network: {subnet_1.network()} {subnet_1.netmask()}"
                        f"\nNetwork Address: {subnet_1.network()}"
                        f"\nBroadcast Address: {subnet_1.broadcast()}"
                        f"\nFirst usable host in subnet: {subnet_1.host_first()}"
                        f"\nLast usable host in subnet: {subnet_1.host_last()}"
                    )

            # IPv6 return message which also is truncated using `.to_compressed()` method
            elif subnet_1.version() == 6:

                if not re.match(
                    RP_IPV6_MORE_THAN_5_CHARACTER_PER_COLON, argumentList[0]
                ):

                    subnet_1_network = subnet_1.network().to_compressed()
                    subnet_1_broadcast = subnet_1.broadcast().to_compressed()
                    subnet_1_host_first = subnet_1.host_first().to_compressed()
                    subnet_1_host_last = subnet_1.host_last().to_compressed()

                    # Creating IPv6 message
                    message = (
                        f"Network: {subnet_1_network}/{subnet_1.subnet()}"
                        f"\nNetwork Address: {subnet_1_network}"
                        f"\nBroadcast Address: {subnet_1_broadcast}"
                        f"\nFirst usable host in subnet: {subnet_1_host_first}"
                        f"\nLast usable host in subnet: {subnet_1_host_last}"
                    )

            # return the either IPv4 message or IPv6
            return message

        # if the user have typed in full netmask after the ip address then parser it here:
        elif len(argumentList) > 1:
            input_validation = re.match(
                RP_IPV4FULLMASK, argumentList[0] + " " + argumentList[1]
            )
            if input_validation:
                # IPv4 or IPv6 address + full mask
                subnet_1 = ipcalc.Network(argumentList[0], argumentList[1])
                if subnet_1.version() == 4:
                    message = (
                        f"Network: {subnet_1.network()} {subnet_1.netmask()}"
                        f"\nNetwork Address: {subnet_1.network()}"
                        f"\nBroadcast Address: {subnet_1.broadcast()}"
                        f"\nFirst usable host in subnet: {subnet_1.host_first()}"
                        f"\nLast usable host in subnet: {subnet_1.host_last()}"
                    )
                return message
            else:
                return error_message

        # if by any means no args were passed, just return an error message.
        else:
            return error_message

    # if the user have typed in an incorrect value this will return an error message
    except Exception as e:
        return error_message


# Checks args list and if passed runs the calculation
# usecase args: 10.10.1.5/23 10.10.2.5/21
def subnet_collision_checker_function():
    try:
        # Sorting the arguments
        subnet_1 = ipcalc.Network(argumentList[0])
        subnet_2 = ipcalc.Network(argumentList[1])

        # The Magic happens here with the collision
        # If any value error occurs then go to exception which will return error message
        check_subnets = subnet_1.check_collision(subnet_2)

        # if either of the inputs are an IPv6 address, then compress the result.
        if subnet_1.version() == 6:
            if subnet_1.to_compressed() == "":
                subnet_1 = f"::/{subnet_1.subnet()}"
            else:
                subnet_1 = f"{subnet_1.to_compressed()}/{subnet_1.subnet()}"

        if subnet_2.version() == 6:
            if subnet_2.to_compressed() == "":
                subnet_2 = f"::/{subnet_2.subnet()}"
            else:
                subnet_2 = f"{subnet_2.to_compressed()}/{subnet_2.subnet()}"

        # Boolean checks and return a message depending on the statement.
        if check_subnets:
            return f"IP address {subnet_1} and {subnet_2} is in the same subnet."
        elif check_subnets == False:
            return f"IP address {subnet_1} and {subnet_2} is not in the same subnet."

    except Exception as e:
        error_message = (
            "Invalid input"
            "\nuse syntax:"
            "\n-ipcalc collision 10.10.10.5/29 10.10.10.16/28"
            "\nor"
            "\n-ipcalc collision 2001:db8:2000::1/64 2001:db8:2001::10/64"
        )
        return error_message


# Regular Expressions
RP_IPV4FULLMASK = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)( )((((255\.){3}(255|254|252|248|240|224|192|128|0+))|((255\.){2}(255|254|252|248|240|224|192|128|0+)\.0)|((255\.)(255|254|252|248|240|224|192|128|0+)(\.0+){2})|((255|254|252|248|240|224|192|128|0+)(\.0+){3})))$"
RP_FULLCIDRv4 = r"^((?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(\/)(0?[1-9]|[12]\d|3[012]) ?)+$"
RP_IPV6_MORE_THAN_5_CHARACTER_PER_COLON = r":?\w{5,}:?"

# __main__ need to fill out this list for the functions to run.
argumentList = []

# subnet_calc_function()
# subnet_collision_checker_function()
