import ipcalc
import re

# Checks args list and chooses which function to use depending on single or multiple inputs
def subnet_calc_function():

    # composing a general error message to return if anything goes wrong
    error_message = (
        "Invalid input."
        "\nUse syntax: "
        "\n-ipc 10.10.10.2/23"
        "\nor"
        "\n-ipc 2001:db8:2001::10/64"
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
                message = (
                    f"Network: {subnet_1.network()} {subnet_1.netmask()}"
                    f"\nNetwork Address: {subnet_1.network()}"
                    f"\nBroadcast Address: {subnet_1.broadcast()}"
                    f"\nFirst usable host in subnet: {subnet_1.host_first()}"
                    f"\nLast usable host in subnet: {subnet_1.host_last()}"
                )

            # IPv6 return message which also is truncated using `.to_compressed()` method
            elif subnet_1.version() == 6:
                # Creating IPv6 message
                message = (
                    f"Network: {subnet_1.network().to_compressed()}/{subnet_1.subnet()}"
                    f"\nNetwork Address: {subnet_1.network().to_compressed()}"
                    f"\nBroadcast Address: {subnet_1.broadcast().to_compressed()}"
                    f"\nFirst usable host in subnet: {subnet_1.host_first().to_compressed()}"
                    f"\nLast usable host in subnet: {subnet_1.host_last().to_compressed()}"
                )

            # return the either IPv4 message or IPv6
            return message

        # if the user have typed in full netmask after the ip address then parser it here:
        elif len(argumentList) > 1:
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

            # IPv6 return message which also is truncated using `.to_compressed()` method
            elif subnet_1.version() == 6:

                # Creating IPv6 message
                message = (
                    f"Network: {subnet_1.network().to_compressed()}/{subnet_1.subnet()}"
                    f"\nNetwork Address: {subnet_1.network().to_compressed()}"
                    f"\nBroadcast Address: {subnet_1.broadcast().to_compressed()}"
                    f"\nFirst usable host in subnet: {subnet_1.host_first().to_compressed()}"
                    f"\nLast usable host in subnet: {subnet_1.host_last().to_compressed()}"
                )

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
            subnet_1 = subnet_1.to_compressed()
        if subnet_2.version() == 6:
            subnet_2 = subnet_2.to_compressed()

        # Boolean checks and return a message depending on the statement.
        if check_subnets:
            return f"IP address {subnet_1} and {subnet_2} is in the same subnet."
        elif check_subnets == False:
            return f"IP address {subnet_1} and {subnet_2} is not the same subnet."

    except Exception as e:
        error_message = (
            "Invalid input"
            "\nuse syntax:"
            "\n-ipcc 10.10.10.5/29 10.10.10.16/28"
            "\nor \n-ipcc 2001:db8:2000::1/64 2001:db8:2001::10/64"
        )
        return error_message



# Checks args list and if passed runs the calculation
# usecase args: 10.10.1.5/23 10.10.2.5/21
def subnet_collision_checker_function():
    if len(argumentList) > 1:
        input_validation = re.match(
            RP_FULLCIDRv4, argumentList[0] + " " + argumentList[1]
        )

        if input_validation:
            subnet_1 = ipcalc.Network(argumentList[0])
            subnet_2 = ipcalc.Network(argumentList[1])
            check_subnets = subnet_1.check_collision(subnet_2)
            if check_subnets:
                return "IP address {} and {} is in the same subnet.".format(
                    subnet_1, subnet_2
                )
            elif check_subnets == False:
                return "IP address {} and {} is not the same subnet.".format(
                    subnet_1, subnet_2
                )
        else:
            error_message = (
                "Invalid input" "\nuse syntax:" "\n-ipcc 10.10.10.5/29 10.10.10.16/28"
            )
            return error_message



# __main__ need to fill out this list for the functions to run.
argumentList = []

# subnet_calc_function()
# subnet_collision_checker_function()
