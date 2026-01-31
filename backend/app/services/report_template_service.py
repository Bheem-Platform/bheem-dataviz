"""
Report Template Service

Business logic for report template management including
template CRUD, versioning, categories, and instances.
"""

from datetime import datetime
from typing import Optional, Any
import uuid
import copy

from app.schemas.report_template import (
    TemplateType, TemplateStatus, PlaceholderType, LayoutType,
    ReportTemplate, ReportTemplateCreate, ReportTemplateUpdate,
    ReportTemplateListResponse,
    TemplateVersion, TemplateVersionListResponse,
    TemplateCategory, TemplateCategoryCreate, TemplateCategoryListResponse,
    TemplateInstance, TemplateInstanceCreate, TemplateInstanceListResponse,
    TemplatePage, TemplateSection, TemplatePlaceholder, TemplateTheme,
    PlaceholderPosition, PlaceholderConfig, PageConfig,
    get_default_theme, get_default_page,
)


class ReportTemplateService:
    """Service for managing report templates."""

    def __init__(self):
        # In-memory stores (replace with database in production)
        self.templates: dict[str, ReportTemplate] = {}
        self.versions: dict[str, TemplateVersion] = {}
        self.categories: dict[str, TemplateCategory] = {}
        self.instances: dict[str, TemplateInstance] = {}

        # Initialize default categories
        self._init_default_categories()
        # Initialize system templates
        self._init_system_templates()

    def _init_default_categories(self):
        """Initialize default template categories."""
        default_categories = [
            ("cat-1", "Business", "Business and financial reports", "briefcase"),
            ("cat-2", "Marketing", "Marketing and campaign reports", "megaphone"),
            ("cat-3", "Sales", "Sales and revenue reports", "chart-bar"),
            ("cat-4", "Operations", "Operational and performance reports", "cog"),
            ("cat-5", "HR", "Human resources reports", "users"),
            ("cat-6", "Custom", "Custom templates", "template"),
        ]

        for i, (cat_id, name, desc, icon) in enumerate(default_categories):
            self.categories[cat_id] = TemplateCategory(
                id=cat_id,
                name=name,
                description=desc,
                icon=icon,
                order=i,
                template_count=0,
            )

    def _init_system_templates(self):
        """Initialize system templates."""
        # Basic Dashboard Report Template
        dashboard_template = ReportTemplate(
            id="sys-tpl-dashboard",
            name="Basic Dashboard Report",
            description="A simple dashboard report template with header, charts, and summary",
            template_type=TemplateType.DASHBOARD,
            category="Business",
            tags=["dashboard", "basic", "starter"],
            user_id="system",
            status=TemplateStatus.PUBLISHED,
            is_public=True,
            is_system=True,
            pages=[
                TemplatePage(
                    id="page-1",
                    name="Dashboard Overview",
                    page_number=1,
                    header=TemplateSection(
                        id="header-1",
                        name="Header",
                        placeholders=[
                            TemplatePlaceholder(
                                id="ph-title",
                                name="Report Title",
                                placeholder_type=PlaceholderType.TEXT,
                                position=PlaceholderPosition(x=20, y=10, width=400, height=40),
                                config=PlaceholderConfig(
                                    placeholder_type=PlaceholderType.TEXT,
                                    default_value="Dashboard Report",
                                ),
                            ),
                            TemplatePlaceholder(
                                id="ph-date",
                                name="Report Date",
                                placeholder_type=PlaceholderType.DATE,
                                position=PlaceholderPosition(x=500, y=10, width=150, height=30),
                                config=PlaceholderConfig(
                                    placeholder_type=PlaceholderType.DATE,
                                    format_string="%B %d, %Y",
                                ),
                            ),
                        ],
                    ),
                    sections=[
                        TemplateSection(
                            id="section-kpi",
                            name="KPI Section",
                            title="Key Metrics",
                            layout=LayoutType.GRID,
                            order=0,
                        ),
                        TemplateSection(
                            id="section-charts",
                            name="Charts Section",
                            title="Visualizations",
                            layout=LayoutType.TWO_COLUMN,
                            order=1,
                        ),
                    ],
                    footer=TemplateSection(
                        id="footer-1",
                        name="Footer",
                        placeholders=[
                            TemplatePlaceholder(
                                id="ph-page",
                                name="Page Number",
                                placeholder_type=PlaceholderType.PAGE_NUMBER,
                                position=PlaceholderPosition(x=300, y=5, width=100, height=20),
                                config=PlaceholderConfig(
                                    placeholder_type=PlaceholderType.PAGE_NUMBER,
                                    format_string="Page {page} of {total}",
                                ),
                            ),
                        ],
                    ),
                ),
            ],
            theme=get_default_theme(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            published_at=datetime.utcnow(),
        )
        self.templates[dashboard_template.id] = dashboard_template

        # Data Table Report Template
        table_template = ReportTemplate(
            id="sys-tpl-table",
            name="Data Table Report",
            description="A report template focused on tabular data with filters",
            template_type=TemplateType.DATA_TABLE,
            category="Business",
            tags=["table", "data", "basic"],
            user_id="system",
            status=TemplateStatus.PUBLISHED,
            is_public=True,
            is_system=True,
            pages=[get_default_page()],
            theme=get_default_theme(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            published_at=datetime.utcnow(),
        )
        self.templates[table_template.id] = table_template

    # Template CRUD Operations

    def create_template(
        self,
        user_id: str,
        data: ReportTemplateCreate,
        organization_id: Optional[str] = None,
    ) -> ReportTemplate:
        """Create a new report template."""
        template_id = f"tpl-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        template = ReportTemplate(
            id=template_id,
            user_id=user_id,
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            template_type=data.template_type,
            category=data.category,
            tags=data.tags,
            status=TemplateStatus.DRAFT,
            version=1,
            pages=data.pages if data.pages else [get_default_page()],
            theme=data.theme if data.theme else get_default_theme(),
            default_filters=data.default_filters or {},
            default_parameters=data.default_parameters or {},
            is_public=data.is_public,
            is_system=False,
            created_at=now,
            updated_at=now,
        )

        self.templates[template_id] = template

        # Update category count
        if data.category:
            for cat in self.categories.values():
                if cat.name == data.category:
                    cat.template_count += 1
                    break

        # Create initial version
        self._create_version(template, user_id, "Initial version")

        return template

    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)

    def list_templates(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        template_type: Optional[TemplateType] = None,
        status: Optional[TemplateStatus] = None,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ReportTemplateListResponse:
        """List templates with filtering."""
        templates = list(self.templates.values())

        # Filter by user/org or public
        if user_id or organization_id:
            templates = [
                t for t in templates
                if t.user_id == user_id or t.organization_id == organization_id or t.is_public
            ]

        if template_type:
            templates = [t for t in templates if t.template_type == template_type]

        if status:
            templates = [t for t in templates if t.status == status]

        if category:
            templates = [t for t in templates if t.category == category]

        if is_public is not None:
            templates = [t for t in templates if t.is_public == is_public]

        if search:
            search_lower = search.lower()
            templates = [
                t for t in templates
                if search_lower in t.name.lower()
                or (t.description and search_lower in t.description.lower())
                or any(search_lower in tag.lower() for tag in t.tags)
            ]

        # Sort by updated_at descending
        templates.sort(key=lambda x: x.updated_at, reverse=True)

        total = len(templates)
        templates = templates[skip:skip + limit]

        return ReportTemplateListResponse(templates=templates, total=total)

    def update_template(
        self,
        template_id: str,
        data: ReportTemplateUpdate,
        user_id: str,
    ) -> Optional[ReportTemplate]:
        """Update a template."""
        template = self.templates.get(template_id)
        if not template or template.is_system:
            return None

        # Track if we need a new version
        needs_version = False
        change_summary_parts = []

        if data.name is not None and data.name != template.name:
            template.name = data.name
            change_summary_parts.append("name updated")

        if data.description is not None:
            template.description = data.description

        if data.category is not None:
            template.category = data.category

        if data.tags is not None:
            template.tags = data.tags

        if data.pages is not None:
            template.pages = data.pages
            needs_version = True
            change_summary_parts.append("pages updated")

        if data.theme is not None:
            template.theme = data.theme
            needs_version = True
            change_summary_parts.append("theme updated")

        if data.default_filters is not None:
            template.default_filters = data.default_filters

        if data.default_parameters is not None:
            template.default_parameters = data.default_parameters

        if data.status is not None:
            old_status = template.status
            template.status = data.status
            if data.status == TemplateStatus.PUBLISHED and old_status != TemplateStatus.PUBLISHED:
                template.published_at = datetime.utcnow()
                change_summary_parts.append("published")

        if data.is_public is not None:
            template.is_public = data.is_public

        template.updated_at = datetime.utcnow()

        # Create new version if structure changed
        if needs_version:
            template.version += 1
            change_summary = ", ".join(change_summary_parts) if change_summary_parts else "Updated"
            self._create_version(template, user_id, change_summary)

        return template

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        template = self.templates.get(template_id)
        if not template or template.is_system:
            return False

        # Delete associated versions
        self.versions = {
            k: v for k, v in self.versions.items()
            if v.template_id != template_id
        }

        # Delete associated instances
        self.instances = {
            k: v for k, v in self.instances.items()
            if v.template_id != template_id
        }

        del self.templates[template_id]
        return True

    def duplicate_template(
        self,
        template_id: str,
        user_id: str,
        new_name: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> Optional[ReportTemplate]:
        """Duplicate a template."""
        original = self.templates.get(template_id)
        if not original:
            return None

        new_id = f"tpl-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        duplicate = ReportTemplate(
            id=new_id,
            user_id=user_id,
            organization_id=organization_id,
            name=new_name or f"{original.name} (Copy)",
            description=original.description,
            template_type=original.template_type,
            category=original.category,
            tags=original.tags.copy(),
            status=TemplateStatus.DRAFT,
            version=1,
            pages=copy.deepcopy(original.pages),
            theme=copy.deepcopy(original.theme),
            default_filters=copy.deepcopy(original.default_filters),
            default_parameters=copy.deepcopy(original.default_parameters),
            is_public=False,
            is_system=False,
            created_at=now,
            updated_at=now,
        )

        self.templates[new_id] = duplicate
        self._create_version(duplicate, user_id, "Duplicated from " + original.name)

        return duplicate

    # Version Management

    def _create_version(
        self,
        template: ReportTemplate,
        user_id: str,
        change_summary: str,
    ) -> TemplateVersion:
        """Create a new version snapshot."""
        version_id = f"ver-{uuid.uuid4().hex[:12]}"

        version = TemplateVersion(
            id=version_id,
            template_id=template.id,
            version=template.version,
            name=template.name,
            description=template.description,
            pages=copy.deepcopy(template.pages),
            theme=copy.deepcopy(template.theme),
            change_summary=change_summary,
            created_by=user_id,
            created_at=datetime.utcnow(),
        )

        self.versions[version_id] = version
        return version

    def list_versions(
        self,
        template_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> TemplateVersionListResponse:
        """List versions for a template."""
        versions = [v for v in self.versions.values() if v.template_id == template_id]
        versions.sort(key=lambda x: x.version, reverse=True)

        total = len(versions)
        versions = versions[skip:skip + limit]

        return TemplateVersionListResponse(versions=versions, total=total)

    def get_version(self, version_id: str) -> Optional[TemplateVersion]:
        """Get a specific version."""
        return self.versions.get(version_id)

    def restore_version(
        self,
        template_id: str,
        version_id: str,
        user_id: str,
    ) -> Optional[ReportTemplate]:
        """Restore a template to a previous version."""
        template = self.templates.get(template_id)
        version = self.versions.get(version_id)

        if not template or not version or version.template_id != template_id:
            return None

        if template.is_system:
            return None

        template.pages = copy.deepcopy(version.pages)
        template.theme = copy.deepcopy(version.theme)
        template.version += 1
        template.updated_at = datetime.utcnow()

        self._create_version(template, user_id, f"Restored to version {version.version}")

        return template

    # Category Management

    def create_category(self, data: TemplateCategoryCreate) -> TemplateCategory:
        """Create a template category."""
        category_id = f"cat-{uuid.uuid4().hex[:8]}"

        category = TemplateCategory(
            id=category_id,
            name=data.name,
            description=data.description,
            icon=data.icon,
            parent_id=data.parent_id,
            order=data.order,
            template_count=0,
        )

        self.categories[category_id] = category
        return category

    def list_categories(
        self,
        parent_id: Optional[str] = None,
    ) -> TemplateCategoryListResponse:
        """List template categories."""
        categories = list(self.categories.values())

        if parent_id is not None:
            categories = [c for c in categories if c.parent_id == parent_id]

        categories.sort(key=lambda x: x.order)

        return TemplateCategoryListResponse(categories=categories, total=len(categories))

    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        category = self.categories.get(category_id)
        if not category or category.template_count > 0:
            return False

        del self.categories[category_id]
        return True

    # Template Instance Management

    def create_instance(
        self,
        user_id: str,
        data: TemplateInstanceCreate,
        organization_id: Optional[str] = None,
    ) -> Optional[TemplateInstance]:
        """Create a template instance for report generation."""
        template = self.templates.get(data.template_id)
        if not template:
            return None

        instance_id = f"inst-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        instance = TemplateInstance(
            id=instance_id,
            template_id=template.id,
            template_version=template.version,
            name=data.name,
            user_id=user_id,
            organization_id=organization_id,
            placeholder_values=data.placeholder_values,
            filters={**template.default_filters, **data.filters},
            parameters={**template.default_parameters, **data.parameters},
            created_at=now,
            updated_at=now,
        )

        self.instances[instance_id] = instance

        # Update template usage count
        template.usage_count += 1

        return instance

    def get_instance(self, instance_id: str) -> Optional[TemplateInstance]:
        """Get instance by ID."""
        return self.instances.get(instance_id)

    def list_instances(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        template_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> TemplateInstanceListResponse:
        """List template instances."""
        instances = list(self.instances.values())

        if user_id:
            instances = [i for i in instances if i.user_id == user_id]

        if organization_id:
            instances = [i for i in instances if i.organization_id == organization_id]

        if template_id:
            instances = [i for i in instances if i.template_id == template_id]

        instances.sort(key=lambda x: x.created_at, reverse=True)

        total = len(instances)
        instances = instances[skip:skip + limit]

        return TemplateInstanceListResponse(instances=instances, total=total)

    def update_instance(
        self,
        instance_id: str,
        placeholder_values: Optional[dict[str, Any]] = None,
        filters: Optional[dict[str, Any]] = None,
        parameters: Optional[dict[str, Any]] = None,
        file_url: Optional[str] = None,
        file_format: Optional[str] = None,
    ) -> Optional[TemplateInstance]:
        """Update a template instance."""
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        if placeholder_values is not None:
            instance.placeholder_values.update(placeholder_values)

        if filters is not None:
            instance.filters.update(filters)

        if parameters is not None:
            instance.parameters.update(parameters)

        if file_url is not None:
            instance.file_url = file_url
            instance.generated_at = datetime.utcnow()

        if file_format is not None:
            instance.file_format = file_format

        instance.updated_at = datetime.utcnow()

        return instance

    def delete_instance(self, instance_id: str) -> bool:
        """Delete an instance."""
        if instance_id in self.instances:
            del self.instances[instance_id]
            return True
        return False


# Global service instance
report_template_service = ReportTemplateService()
