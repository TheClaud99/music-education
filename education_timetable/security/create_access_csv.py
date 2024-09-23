import csv
import os

FULL_ACCESS = (1, 1, 1, 1)
READONLY = (1, 0, 0, 0)

# Lista dei permessi per i modelli
# 1 posto => module
# 2 posto => model
# 3 posto => dict con la seguente struttura:
#   - chiave ruolo (la stessa del dict ROLES)
#   - lista di permessi con il seguente ordine: (read, write, create, unlink, options)
# fmt: off
MODELS = (
    ("education_timetable", "education.day", {"manager": FULL_ACCESS, "user": READONLY}),
    ("education_timetable", "education.session.attendance", {"manager": FULL_ACCESS, "user": READONLY}),
    ("education_timetable", "education.session.presence.line", {"manager": FULL_ACCESS, "user": READONLY}),
    ("education_timetable", "education.session.presence", {"manager": FULL_ACCESS, "user": READONLY}),
    ("education_timetable", "education.session", {"manager": FULL_ACCESS, "user": READONLY}),
    ("education_timetable", "education.timetable.line", {"manager": FULL_ACCESS, "user": READONLY}),
    ("calendar", "calendar.event", {"manager": FULL_ACCESS, "user": READONLY, "all_employee": (1, 0, 0, 0, {"override": True})}),
)
# fmt: on

# Lista di ruoli
# 1 livello => chiave ruolo
# 2 livello => lista con la seguente struttura: (modulo, nome gruppo)
ROLES = {
    # "admin": ("sofidel_activities", "group_sofidel_activities_admin"),
    "manager": ("education", "education_manager"),
    "user": ("education", "education_user"),
    "all_employee": ("base", "group_user"),
}


def main(models, roles):
    file_csv = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../security/ir.model.access.csv")
    )
    with open(file_csv, "w") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(
            [
                "id",
                "name",
                "model_id:id",
                "group_id:id",
                "perm_read",
                "perm_write",
                "perm_create",
                "perm_unlink",
            ]
        )

        for model in models:
            module_name = model[0]
            model_name = model[1]
            model_name_underscored = model[1].replace(".", "_")
            for role_key, perms in model[2].items():
                role_module = roles[role_key][0]
                role_name = roles[role_key][1]
                options = {}
                if len(perms) > 4:
                    options = perms[4]

                if options.get("override"):
                    row_id = "%s.access_%s_%s" % (
                        module_name,
                        model_name_underscored,
                        role_key,
                    )
                else:
                    row_id = "access_%s_%s" % (model_name_underscored, role_key)
                writer.writerow(
                    [
                        row_id,
                        model_name,
                        "%s.model_%s" % (module_name, model_name_underscored),
                        "%s.%s" % (role_module, role_name),
                        perms[0],
                        perms[1],
                        perms[2],
                        perms[3],
                    ]
                )


if __name__ == "__main__":
    main(MODELS, ROLES)
