import csv

from django.http import Http404, HttpResponse
from django.template.defaultfilters import striptags

from cdhweb.pages.blocks.accordion_block import ProjectAccordion
from cdhweb.projects.models import Project


def export_project_accordion_csv_view(request, page_id):
    """Export ProjectAccordion contents for a single project to CSV"""
    try:
        project = Project.objects.get(id=page_id)
    except Project.DoesNotExist:
        raise Http404("Project not found")

    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="project_{project.slug}_accordion.csv"'

    writer = csv.writer(response)
    writer.writerow(["Project Title", "Accordion Heading", "Body Text"])

    # Check if project has accordion content
    for block in project.accordion:
        if block.block_type == "accordion":
            accordion_data = block.value

            if "accordion_items" in accordion_data:
                for item in accordion_data["accordion_items"]:
                    heading_key = item.get("heading", "")
                    heading_label = dict(ProjectAccordion.AccordionTitles.choices).get(
                        heading_key, heading_key
                    )
                    body = striptags(item.get("body", ""))
                    writer.writerow([project.title, heading_label, body])

    return response
