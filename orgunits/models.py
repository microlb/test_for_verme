"""
Copyright 2020 ООО «Верме»
"""

from django.db import models


class OrganizationQuerySet(models.QuerySet):
    def tree_downwards(self, root_org_id):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type root_org_id: int
        """

        id = root_org_id
        child = Organization.objects.raw('''with cte as (
                                                select
                                                    id,
                                                    parent_id,
                                                    '/' || name as name
                                                from orgunits_organization where id = %s
                                                union all
                                                select
                                                    orgunits_organization.id,
                                                    orgunits_organization.parent_id,
                                                    cte.name || '/' || orgunits_organization.name
                                                from cte, orgunits_organization on orgunits_organization.parent_id = cte.id
                                                )
                                                select orgunits_organization.id, orgunits_organization.name, orgunits_organization.parent_id
                                                from orgunits_organization, cte
                                                Where orgunits_organization.id = cte.id;''', [id])
        return child

    def tree_upwards(self, child_org_id):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type child_org_id: int
        """

        id = child_org_id
        parents = Organization.objects.raw('''with cte as (
                                                        select
                                                            id,
                                                            parent_id,
                                                            '/' || name as name
                                                        from orgunits_organization where id = %s
                                                        union all
                                                        select
                                                            orgunits_organization.id,
                                                            orgunits_organization.parent_id,
                                                            cte.name || '/' || orgunits_organization.name
                                                        from cte, orgunits_organization on orgunits_organization.id = cte.parent_id
                                                        )
                                                        select orgunits_organization.id, orgunits_organization.name, orgunits_organization.parent_id
                                                        from orgunits_organization, cte
                                                        Where orgunits_organization.id = cte.id;''', [id])

        return parents


class Organization(models.Model):
    """ Организаци """

    objects = OrganizationQuerySet.as_manager()

    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name="Название")
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name="Код")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, verbose_name="Вышестоящая организация",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Организации"   # было ОрганизациЯ
        verbose_name = "Организация"          # было ОрганизациИ

    def parents(self):
        """
        Возвращает всех родителей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_upwards()

        :rtype: django.db.models.QuerySet
        """
        parents = Organization.objects.tree_upwards(self.id)
        set_id = set()
        for parent in parents:
            if parent.id != self.id:
                set_id.add(parent.id)
        parents_set = Organization.objects.filter(id__in=set_id)
        return parents_set

    def children(self):
        """
        Возвращает всех детей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_downwards()

        :rtype: django.db.models.QuerySet
        """
        children = Organization.objects.tree_downwards(self.id)
        set_id = set()
        for child in children:
            if child.id != self.id:
                set_id.add(child.id)
        children_set = Organization.objects.filter(id__in=set_id)
        return children_set