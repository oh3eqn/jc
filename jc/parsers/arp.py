"""jc - JSON CLI output utility arp Parser

Usage:

    specify --arp as the first argument if the piped input is coming from:

    arp
      or
    arp -a

Compatibility:

    'linux', 'aix', 'freebsd', 'darwin'

Examples:

    $ arp | jc --arp -p
    [
      {
        "address": "192.168.71.254",
        "hwtype": "ether",
        "hwaddress": "00:50:56:f0:98:26",
        "flags_mask": "C",
        "iface": "ens33"
      },
      {
        "address": "gateway",
        "hwtype": "ether",
        "hwaddress": "00:50:56:f7:4a:fc",
        "flags_mask": "C",
        "iface": "ens33"
      }
    ]

    $ arp | jc --arp -p -r
    [
      {
        "address": "gateway",
        "hwtype": "ether",
        "hwaddress": "00:50:56:f7:4a:fc",
        "flags_mask": "C",
        "iface": "ens33"
      },
      {
        "address": "192.168.71.254",
        "hwtype": "ether",
        "hwaddress": "00:50:56:fe:7a:b4",
        "flags_mask": "C",
        "iface": "ens33"
      }
    ]

    $ arp -a | jc --arp -p
    [
      {
        "name": null,
        "address": "192.168.71.254",
        "hwtype": "ether",
        "hwaddress": "00:50:56:f0:98:26",
        "iface": "ens33"
      },
      {
        "name": "gateway",
        "address": "192.168.71.2",
        "hwtype": "ether",
        "hwaddress": "00:50:56:f7:4a:fc",
        "iface": "ens33"
      }
    ]

    $ arp -a | jc --arp -p -r
    [
      {
        "name": "?",
        "address": "192.168.71.254",
        "hwtype": "ether",
        "hwaddress": "00:50:56:fe:7a:b4",
        "iface": "ens33"
      },
      {
        "name": "_gateway",
        "address": "192.168.71.2",
        "hwtype": "ether",
        "hwaddress": "00:50:56:f7:4a:fc",
        "iface": "ens33"
      }
    ]
"""
import jc.utils
import jc.parsers.universal


class info():
    version = '1.1'
    description = 'arp command parser'
    author = 'Kelly Brazil'
    author_email = 'kellyjonbrazil@gmail.com'

    # compatible options: linux, darwin, cygwin, win32, aix, freebsd
    compatible = ['linux', 'aix', 'freebsd', 'darwin']
    magic_commands = ['arp']


__version__ = info.version


def process(proc_data):
    """
    Final processing to conform to the schema.

    Parameters:

        proc_data:   (dictionary) raw structured data to process

    Returns:

        List of dictionaries. Structured data with the following schema:

        [
          {
            "name":       string,
            "address":    string,
            "hwtype":     string,
            "hwaddress":  string,
            "flags_mask": string,
            "iface":      string
          }
        ]
    """

    # in BSD style, change name to null if it is a question mark
    for entry in proc_data:
        if 'name' in entry and entry['name'] == '?':
            entry['name'] = None

    return proc_data


def parse(data, raw=False, quiet=False):
    """
    Main text parsing function

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) output preprocessed JSON if True
        quiet:       (boolean) suppress warning messages if True

    Returns:

        List of dictionaries. Raw or processed structured data.
    """
    if not quiet:
        jc.utils.compatibility(__name__, info.compatible)

    cleandata = data.splitlines()

    # remove final Entries row if -v was used
    if cleandata[-1].find('Entries:') == 0:
        cleandata.pop(-1)

    # detect if osx style was used
    if cleandata[0].find(' ifscope ') != -1:
        raw_output = []
        for line in cleandata:
            line = line.split()
            output_line = {}
            output_line['name'] = line[0]
            output_line['address'] = line[1].lstrip('(').rstrip(')')
            output_line['hwtype'] = line[-1].lstrip('[').rstrip(']')
            output_line['hwaddress'] = line[3]
            output_line['iface'] = line[5]
            raw_output.append(output_line)

        if raw:
            return raw_output
        else:
            return process(raw_output)

    # detect if linux style was used
    elif cleandata[0].find('Address') == 0:

        # fix header row to change Flags Mask to flags_mask
        cleandata[0] = cleandata[0].replace('Flags Mask', 'flags_mask')
        cleandata[0] = cleandata[0].lower()

        raw_output = jc.parsers.universal.simple_table_parse(cleandata)

        if raw:
            return raw_output
        else:
            return process(raw_output)

    # otherwise, try bsd style
    else:
        raw_output = []
        for line in cleandata:
            line = line.split()
            output_line = {
                'name': line[0],
                'address': line[1].lstrip('(').rstrip(')'),
                'hwtype': line[4].lstrip('[').rstrip(']'),
                'hwaddress': line[3],
                'iface': line[6],
            }
            raw_output.append(output_line)

        if raw:
            return raw_output
        else:
            return process(raw_output)
