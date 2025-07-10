import csv

from django.http import HttpResponse
from django.template.defaultfilters import striptags

from cdhweb.pages.blocks.accordion_block import ProjectAccordion
from cdhweb.projects.models import Project


def export_accordion_csv_view(request):
    """Export accordion data for all projects"""

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="project_accordion.csv"'

    writer = csv.writer(response)
    writer.writerow(["Project Title", "Accordion Heading", "Body Text"])

    projects = Project.objects.live()

    for project in projects:
        # Check if project has accordion content
        for block in project.accordion:
            if block.block_type == "accordion":
                accordion_data = block.value

                if "accordion_items" in accordion_data:
                    for item in accordion_data["accordion_items"]:
                        heading_key = item.get("heading", "")
                        heading_label = dict(
                            ProjectAccordion.AccordionTitles.choices
                        ).get(heading_key, heading_key)
                        body = striptags(item.get("body", ""))
                        writer.writerow([project.title, heading_label, body])

    return response
