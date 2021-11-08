"""Workflow patch script.

This script injects the MDTOOL_LINK in the vanilla Archivematica workflow file.

Usage:

  $ patcher /src/src/MCPServer/lib/assets/workflow.json -o /tmp/patched-workflow.json

We go from this:

    LINK_A --------> LINK_B

To this:

    LINK_A --------> INJECTED -------> LINK_B

Which means that we need to:

1. Inject the chain link.
2. Make it point to the original LINK_B.
3. Update LINK_A so it goes to our new chain link after execution.
"""

from argparse import ArgumentParser
import json
import uuid
import sys
import contextlib


if sys.version_info[0] == 2:
    raise Exception("Please, use Python 3.")


# List of chain links using create_mets_v2.
# This is only going to work with the vanilla Archivematica workflow.
CREATE_METS_V2_LINKS = (
    {
        "id": "18c37bff-fce9-4b40-a50a-022ea0386f1a",
        "next_id": "523c97cc-b267-4cfb-8209-d99e523bf4b3"
    },
    {
        "id": "53e14112-21bb-46f0-aed3-4e8c2de6678f",
        "next_id": "3e25bda6-5314-4bb4-aa1e-90900dce887d"
    },
    {
        "id": "ccf8ec5c-3a9a-404a-a7e7-8f567d3b36a0",
        "next_id": "523c97cc-b267-4cfb-8209-d99e523bf4b3"
    },
)

# Definition of our new chain link.
MDTOOL_LINK = {
    "config": {
        "@manager": "linkTaskManagerDirectories",
        "arguments": "--sipUUID \"%SIPUUID%\" --basePath \"%SIPDirectory%\"",
        "execute": "md_writer_v0.0",
        "filter_file_end": None,
        "filter_file_start": None,
        "filter_subdir": None,
        "stderr_file": None,
        "stdout_file": None
    },
    "description": {
        "en": "Run md_writer tool"
    },

    "exit_codes": {
        "0": {
            "job_status": "Completed successfully",
            "link_id": "~~~~~~~~~ THIS IS GENERATED DYNAMICALLY ~~~~~~~~~~~~~"
        }
    },

    # Fallback config when the execution of this chain link fails.
    # 7d728c39 is "Email fail report", used in many other places in workflow
    # to exit processing.
    "fallback_job_status": "Failed",
    "fallback_link_id": "7d728c39-395f-4892-8193-92f086c0546f",

    "group": {
        "en": "Generate AIP METS"
    }
}


def generate_link(next_id):
    link = MDTOOL_LINK.copy()
    link["exit_codes"]["0"]["link_id"] = next_id

    return link


def update_link_destination(source_link, dest_id):
    source_link["exit_codes"]["0"]["link_id"] = dest_id


@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def main(workflow_file, output_file=None):
    """
    1. Open ``workflow_file`` and decoding its contents (JSON)
    2. Insert our new chain link (should be defined somewhere in this script)
    3. Inject the new chain link into the existing workflow chain, e.g. between links 123 and abc.
    4. Save the document into ``output_file``.
    """
    with open(workflow_file) as fd:
       workflow = json.load(fd)

    for create_mets_v2_link in CREATE_METS_V2_LINKS:
        link_id = create_mets_v2_link["id"]
        next_id = create_mets_v2_link["next_id"]

        # Generate new link that we're injecting with its own UUID.
        gen_id = str(uuid.uuid4())
        link = generate_link(next_id)

        # Inject link.
        workflow["links"][gen_id] = link

        # Update original link so it goes to our link after it executes.
        update_link_destination(workflow["links"][link_id], gen_id)

    with smart_open(output_file) as writer:
        writer.write(json.dumps(workflow, ensure_ascii="False", sort_keys=True, indent=4))

    # if output_file in ("-", "", None):
    #     writer = sys.stdout
    # else:
    #     # TODO: close
    #     writer = open(output_file, "w")
    #
    # writer.write(json.dumps(workflow))





if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument("workflow_file", metavar="workflow-file", help="Original workflow file")
    parser.add_argument("-o", "--output", dest="output_file", help="Write location")
    args = parser.parse_args()
    main(args.workflow_file, args.output_file)

