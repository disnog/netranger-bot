import ipcalc
import re


# subnet calc with full netmask
def subnet_calc(x, y):
    subnet_1 = ipcalc.Network(x, y)
    print("Network:", subnet_1.network(), subnet_1.netmask())
    print("Network Adress:", subnet_1.network())
    print("Broadcast adress:", subnet_1.broadcast())
    print("First usable host in subnet:", subnet_1.host_first())
    print("Last usable host in subnet:", subnet_1.host_last())


# subnet calc with cidr notation
def subnet_calc_1(x):
    subnet_1 = ipcalc.Network(x)
    print("Network:", subnet_1.network(), subnet_1.netmask())
    print("Network Adress:", subnet_1.network())
    print("Broadcast adress:", subnet_1.broadcast())
    print("First usable host in subnet:", subnet_1.host_first())
    print("Last usable host in subnet:", subnet_1.host_last())


# Checks args list and chooses which function to use depending on single or multiple inputs
def subnet_calc_function():
    if len(argumentList) == 1:
        # IPv4 address with CIDRv4
        result = re.match(RP_FULLCIDRv4, argumentList[0])
        if result:
            subnet_calc_1(argumentList[0])
        else:
            print("Invalid input.", "Use syntax:", "10.10.10.2/23", "or", "10.10.10.2 255.255.254.0", sep="\n")

    if len(argumentList) > 1:
        # IPv4 address + full mask
        result = re.match(RP_IPV4FULLMASK, argumentList[0] + " " + argumentList[1])
        if result:
            subnet_calc(argumentList[0], argumentList[1])
        else:
            print("Invalid input.", "Use syntax:", "-ipc 10.10.10.2/23", "or", "-ipc 10.10.10.2 255.255.254.0", sep="\n")

# Subnet collision checker calculator
def subnet_collision_checker(x, y):
    subnet_1 = ipcalc.Network(x)
    subnet_2 = ipcalc.Network(y)
    result = subnet_1.check_collision(subnet_2)
    if result:
        print("IP address {} and {} is in the same subnet.".format(subnet_1, subnet_2))
    elif result == False:
        print("IP address {} and {} is not in the same subnet.".format(subnet_1, subnet_2))


# Checks args list and if passed runs the calculation
# usecase args: 10.10.1.5/23 10.10.2.5/21
def subnet_collision_checker_function():
    if len(argumentList) > 1:
        value_check = re.match(RP_FULLCIDRv4, argumentList[0] + " " + argumentList[1])

        if value_check:
            subnet_collision_checker(argumentList[0], argumentList[1])

        else:
            print("Invalid input, use syntax:", "-ipcc 10.10.10.5/29 10.10.10.16/28", sep="\n")
#

RP_IPV4FULLMASK = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)( )((((255\.){3}(255|254|252|248|240|224|192|128|0+))|((255\.){2}(255|254|252|248|240|224|192|128|0+)\.0)|((255\.)(255|254|252|248|240|224|192|128|0+)(\.0+){2})|((255|254|252|248|240|224|192|128|0+)(\.0+){3})))$'
RP_FULLCIDRv4 = r'^((?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(\/)(0?[1-9]|[12]\d|3[012]) ?)+$'
