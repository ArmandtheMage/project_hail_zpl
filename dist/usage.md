# Hail ZPL

## .env
Please edit the needed part.
Inside there are the variables that are personal or generally to not be shared

**Note:** the file is not included in the distributed files.
> **Be sure to update your PAT**

## gui
Is a simple gui that will simplify the extraction and generation of the report xml for a zpl.

The gui has 3 areas:
- save & project information
- testplan
- changelog/issues

### save & project information
here is possible to:
- select throught a navigation window the folder where to save the generated report.
- choose by a drop-down menu the project where all the action will be performed

### testplan
here inserting a specific test plan id, is possible to extract all the test setted relative to it.
In possible filter the extraction adding a list or single test suites, in none all the test suites are extracted

### changelog/issue
here is possible set a version to work with and an area path to limit the research
**Note:** the changelog part is linked to the issue, so write in changelog will fill even the issue's fields
> for now only the changelog trigger the issue not viceversa

## report
the common interface of the zpl is mimic to compliance, and are add a color cell fill rule to highlight the pass and fail report.
