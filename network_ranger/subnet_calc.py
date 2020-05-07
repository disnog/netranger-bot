import ipcalc
import re

# Checks args list and chooses which function to use depending on single or multiple inputs
def subnet_calc_function():
    if len(argumentList) == 1:
        # IPv4 address with CIDRv4
        input_validation = re.match(RP_FULLCIDRv4, argumentList[0])
        if input_validation:
            subnet_1 = ipcalc.Network(argumentList[0])
            message = (
                f"Network: {subnet_1.network()} {subnet_1.netmask()}"
                f"\nNetwork Address: {subnet_1.network()}"
                f"\nBroadcast Address: {subnet_1.broadcast()}"
                f"\nFirst usable host in subnet: {subnet_1.host_first()}"
                f"\nLast usable host in subnet: {subnet_1.host_last()}"
            )
            return message

        else:
            error_message = (
                "Invalid input."
                "\nUse syntax: "
                "\n-ipc 10.10.10.2/23"
                "\nor"
                "\n-ipc 10.10.10.2 255.255.254.0"
            )
            return error_message

    if len(argumentList) > 1:
        # IPv4 address + full mask
        result = re.match(RP_IPV4FULLMASK, argumentList[0] + " " + argumentList[1])
        if result:
            subnet_1 = ipcalc.Network(argumentList[0], argumentList[1])
            message = (
                f"Network: {subnet_1.network()} {subnet_1.netmask()}"
                f"\nNetwork Address: {subnet_1.network()}"
                f"\nBroadcast Address: {subnet_1.broadcast()}"
                f"\nFirst usable host in subnet: {subnet_1.host_first()}"
                f"\nLast usable host in subnet: {subnet_1.host_last()}"
            )
            return message

        else:
            error_message = (
                "Invalid input."
                "\nUse syntax: "
                "\n-ipc 10.10.10.2/23"
                "\nor"
                "\n-ipc 10.10.10.2 255.255.254.0"
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


# Regular Expressions
RP_IPV4FULLMASK = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)( )((((255\.){3}(255|254|252|248|240|224|192|128|0+))|((255\.){2}(255|254|252|248|240|224|192|128|0+)\.0)|((255\.)(255|254|252|248|240|224|192|128|0+)(\.0+){2})|((255|254|252|248|240|224|192|128|0+)(\.0+){3})))$"
RP_FULLCIDRv4 = r"^((?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(\/)(0?[1-9]|[12]\d|3[012]) ?)+$"

# __main__ need to fill out this list for the functions to run.
argumentList = []

# subnet_calc_function()
# subnet_collision_checker_function()
