# Generated by Django 5.0.5 on 2024-05-13 03:20

import wagtail.blocks
import wagtail.fields
from django.db import migrations

import cdhweb.pages.blocks.download_block


class Migration(migrations.Migration):
    dependencies = [
        ("cdhpages", "0015_alter_homepage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "download_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        help_text="Heading for document block",
                                        max_length=80,
                                        required=False,
                                    ),
                                ),
                                (
                                    "description",
                                    wagtail.blocks.TextBlock(
                                        help_text="A description to display with the download file (150 characters maximum).",
                                        max_length=150,
                                        required=False,
                                    ),
                                ),
                                (
                                    "documents",
                                    wagtail.blocks.ListBlock(
                                        cdhweb.pages.blocks.download_block.FileBlock,
                                        help_text="Upload at least 1 and maximum 10 files. Each file size should be less than 5MB.",
                                        max_num=10,
                                        min_num=1,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "cta_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "introduction",
                                    wagtail.blocks.TextBlock(
                                        help_text="Short introduction to the action you want users to take. Ideal: 80 characters or less (Max: 100 characters).",
                                        max_length=100,
                                        required=False,
                                    ),
                                ),
                                (
                                    "cta_buttons",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "internal_link",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "page",
                                                            wagtail.blocks.PageChooserBlock(),
                                                        ),
                                                        (
                                                            "link_text",
                                                            wagtail.blocks.CharBlock(
                                                                label="Button text",
                                                                max_length=40,
                                                                required=True,
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                            ),
                                            (
                                                "external_link",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "link_url",
                                                            wagtail.blocks.URLBlock(
                                                                label="URL"
                                                            ),
                                                        ),
                                                        (
                                                            "link_text",
                                                            wagtail.blocks.CharBlock(
                                                                label="Button text",
                                                                max_length=40,
                                                                required=True,
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                            ),
                                        ],
                                        max_num=2,
                                        min_num=1,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "accordion_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "accordion_items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                (
                                                    "heading",
                                                    wagtail.blocks.CharBlock(
                                                        max_length=80,
                                                        required=True,
                                                        verbose_name="Accordion Title",
                                                    ),
                                                ),
                                                (
                                                    "body",
                                                    wagtail.blocks.RichTextBlock(
                                                        features=[
                                                            "bold",
                                                            "link",
                                                            "ol",
                                                            "ul",
                                                            "document-link",
                                                            "image",
                                                            "h4",
                                                        ]
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                )
                            ]
                        ),
                    ),
                    (
                        "block_quote",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.blocks.TextBlock(
                                        help_text="Add and style a longer form quotation to make it stand out from the rest of your text. Used if a quote is longer than 40 words",
                                        required=True,
                                    ),
                                )
                            ]
                        ),
                    ),
                    (
                        "video_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "video",
                                    wagtail.blocks.URLBlock(
                                        help_text="A YouTube URL. Link to a specifc video or playlist."
                                    ),
                                ),
                                (
                                    "accessibility_description",
                                    wagtail.blocks.CharBlock(
                                        help_text="Use this to describe the video. It is used as an accessibility attribute mainly for screen readers.",
                                        required=False,
                                    ),
                                ),
                                (
                                    "transcript",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "link", "document-link"],
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "pull_quote",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.blocks.TextBlock(
                                        help_text='Pull a small section of content out as an "aside" to give it emphasis.',
                                        max_length=100,
                                        required=True,
                                    ),
                                ),
                                (
                                    "attribution",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "link"],
                                        help_text="Optional attribution",
                                        max_length=60,
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "note",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.TextBlock(
                                        help_text="Optional heading", required=False
                                    ),
                                ),
                                (
                                    "message",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "link", "ul", "ol"],
                                        help_text="Note message up to 750 chars",
                                        max_length=750,
                                        required=True,
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                blank=True,
                help_text="Put content for the body of the page here. Start with using the + button.",
                use_json_field=True,
                verbose_name="Page content",
            ),
        ),
    ]