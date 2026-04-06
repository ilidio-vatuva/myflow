from oauth import generate_oauth_url
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from translations import t


MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("📋 Menu")]],
    resize_keyboard=True,
    is_persistent=True
)

def _hours_label(n, language):
    unit = t("btn_hour", language) if n == 1 else t("btn_hours", language)
    return f"⏰ {n} {unit}"

async def send_oauth_prompt(sender, telegram_user_id, message, language="en-US"):
    auth_url = generate_oauth_url(telegram_user_id)
    keyboard = [[InlineKeyboardButton(t("btn_connect_calendar", language), url=auth_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(message, reply_markup=reply_markup)

async def send_projects_prompt(sender, projects, language="en-US"):
    keyboard = []
    for project in sorted(projects, key=lambda project: project.name):
        inline_keyboard = [InlineKeyboardButton(f"📋 {project.name}", callback_data=f"project_{project.id}")]
        keyboard.append(inline_keyboard)
    keyboard.append([InlineKeyboardButton(t("btn_new_project", language), callback_data="new_project")])
    keyboard.append([InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("pick_project", language), reply_markup=reply_markup)

async def send_goals_prompt(sender, goals, language="en-US"):
    keyboard = []
    for goal in sorted(goals, key=lambda goal: goal.name):
        inline_keyboard = [InlineKeyboardButton(f"🎯 {goal.name}", callback_data=f"goalId_{goal.id}")]
        keyboard.append(inline_keyboard)
    keyboard.append([InlineKeyboardButton(t("btn_new_goal", language), callback_data="new_goal")])
    keyboard.append([InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("pick_goal", language), reply_markup=reply_markup)

async def send_planning_projects_list(sender, projects, language="en-US"):
    keyboard = []
    for project in projects:
        keyboard.append([InlineKeyboardButton(
            f"📌 {project.name}", 
            callback_data=f"plan_project_{project.id}"
        )])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("planning_pick_project", language), reply_markup=reply_markup)

async def send_project_planning_menu(sender, project, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton("🤖 " + t("btn_suggest_task", language), callback_data=f"plan_suggest_{project.id}"),
            InlineKeyboardButton("✏️ " + t("btn_create_myself", language), callback_data=f"plan_create_{project.id}"),
            InlineKeyboardButton("⏭️ " + t("btn_skip", language), callback_data=f"plan_skip_{project.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(f"📌 {project.name}", reply_markup=reply_markup)

async def send_goal_importance_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_importance_low", language), callback_data="goal_importance_1"),
            InlineKeyboardButton(t("btn_importance_medium", language), callback_data="goal_importance_2"),
            InlineKeyboardButton(t("btn_importance_high", language), callback_data="goal_importance_3")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("goal_importance", language), reply_markup=reply_markup)

async def send_edit_goal_importance_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_importance_low", language), callback_data="edit_goal_importance_1"),
            InlineKeyboardButton(t("btn_importance_medium", language), callback_data="edit_goal_importance_2"),
            InlineKeyboardButton(t("btn_importance_high", language), callback_data="edit_goal_importance_3")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("goal_importance", language), reply_markup=reply_markup)

async def send_deadline_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_today", language), callback_data="deadline_today"),
            InlineKeyboardButton(t("btn_tomorrow", language), callback_data="deadline_tomorrow")
        ],
        [
            InlineKeyboardButton(t("btn_this_week", language), callback_data="deadline_this_week"),
            InlineKeyboardButton(t("btn_this_month", language), callback_data="deadline_this_month"),
            InlineKeyboardButton(t("btn_no_deadline", language), callback_data="deadline_none")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("pick_deadline", language), reply_markup=reply_markup)

async def send_project_daily_hours_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(_hours_label(1, language), callback_data="hours_1"),
            InlineKeyboardButton(_hours_label(2, language), callback_data="hours_2"),
            InlineKeyboardButton(_hours_label(3, language), callback_data="hours_3")
        ],
        [
            InlineKeyboardButton(_hours_label(4, language), callback_data="hours_4"),
            InlineKeyboardButton(_hours_label(5, language), callback_data="hours_5"),
            InlineKeyboardButton(_hours_label(6, language), callback_data="hours_6")
        ],
        [
            InlineKeyboardButton(_hours_label(7, language), callback_data="hours_7"),
            InlineKeyboardButton(_hours_label(8, language), callback_data="hours_8")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("project_time_spent", language), reply_markup=reply_markup)

async def send_project_weekly_hours_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(_hours_label(5, language), callback_data="hours_5"),
            InlineKeyboardButton(_hours_label(6, language), callback_data="hours_6"),
            InlineKeyboardButton(_hours_label(7, language), callback_data="hours_7")
        ],
        [
            InlineKeyboardButton(_hours_label(8, language), callback_data="hours_8"),
            InlineKeyboardButton(_hours_label(10, language), callback_data="hours_10"),
            InlineKeyboardButton(_hours_label(20, language), callback_data="hours_20"),
            InlineKeyboardButton(_hours_label(40, language), callback_data="hours_40")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("project_time_spent", language), reply_markup=reply_markup)

async def send_project_monthly_hours_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(_hours_label(20, language), callback_data="hours_20"),
            InlineKeyboardButton(_hours_label(40, language), callback_data="hours_40"),
            InlineKeyboardButton(_hours_label(60, language), callback_data="hours_60")
        ],
        [
            InlineKeyboardButton(_hours_label(80, language), callback_data="hours_80"),
            InlineKeyboardButton(_hours_label(100, language), callback_data="hours_100"),
            InlineKeyboardButton(_hours_label(150, language), callback_data="hours_150"),
            InlineKeyboardButton(_hours_label(200, language), callback_data="hours_200")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("project_time_spent", language), reply_markup=reply_markup)

async def send_edit_project_hours_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(_hours_label(1, language), callback_data="edit_hours_1"),
            InlineKeyboardButton(_hours_label(2, language), callback_data="edit_hours_2"),
            InlineKeyboardButton(_hours_label(3, language), callback_data="edit_hours_3")
        ],
        [
            InlineKeyboardButton(_hours_label(4, language), callback_data="edit_hours_4"),
            InlineKeyboardButton(_hours_label(5, language), callback_data="edit_hours_5"),
            InlineKeyboardButton(_hours_label(6, language), callback_data="edit_hours_6")
        ],
        [
            InlineKeyboardButton(_hours_label(7, language), callback_data="edit_hours_7"),
            InlineKeyboardButton(_hours_label(8, language), callback_data="edit_hours_8"),
            InlineKeyboardButton(_hours_label(10, language), callback_data="edit_hours_10")
        ],
        [
            InlineKeyboardButton(_hours_label(20, language), callback_data="edit_hours_20"),
            InlineKeyboardButton(_hours_label(40, language), callback_data="edit_hours_40"),
            InlineKeyboardButton(_hours_label(60, language), callback_data="edit_hours_60")
        ],
        [
            InlineKeyboardButton(_hours_label(80, language), callback_data="edit_hours_80"),
            InlineKeyboardButton(_hours_label(100, language), callback_data="edit_hours_100"),
            InlineKeyboardButton(_hours_label(150, language), callback_data="edit_hours_150"),
            InlineKeyboardButton(_hours_label(200, language), callback_data="edit_hours_200")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("project_time_spent", language), reply_markup=reply_markup)

async def send_project_frequency_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_daily", language), callback_data="frequency_daily"),
            InlineKeyboardButton(t("btn_weekly", language), callback_data="frequency_weekly"),
            InlineKeyboardButton(t("btn_monthly", language), callback_data="frequency_monthly")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("project_frequency", language), reply_markup=reply_markup)

async def send_edit_project_frequency_prompt(sender, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_daily", language), callback_data="edit_frequency_daily"),
            InlineKeyboardButton(t("btn_weekly", language), callback_data="edit_frequency_weekly"),
            InlineKeyboardButton(t("btn_monthly", language), callback_data="edit_frequency_monthly")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("project_frequency", language), reply_markup=reply_markup)

async def send_due_date_prompt(sender, language="en-US"):
    keyboard = [
    [
        InlineKeyboardButton(t("btn_1_month", language), callback_data="due_date_1month"),
        InlineKeyboardButton(t("btn_3_months", language), callback_data="due_date_3months"),
        InlineKeyboardButton(t("btn_6_months", language), callback_data="due_date_6months"),
    ],
    [
        InlineKeyboardButton(t("btn_1_year", language), callback_data="due_date_1year"),
        InlineKeyboardButton(t("btn_no_due_date", language), callback_data="due_date_none")
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("pick_due_date", language), reply_markup=reply_markup)

async def send_edit_due_date_prompt(sender, language="en-US"):
    keyboard = [
    [
        InlineKeyboardButton(t("btn_1_month", language), callback_data="edit_due_date_1month"),
        InlineKeyboardButton(t("btn_3_months", language), callback_data="edit_due_date_3months"),
        InlineKeyboardButton(t("btn_6_months", language), callback_data="edit_due_date_6months"),
    ],
    [
        InlineKeyboardButton(t("btn_1_year", language), callback_data="edit_due_date_1year"),
        InlineKeyboardButton(t("btn_no_due_date", language), callback_data="edit_due_date_none")
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("pick_due_date", language), reply_markup=reply_markup)

async def send_preferred_language_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 English", callback_data="language_en-US"),
            InlineKeyboardButton("🇵🇹 Português", callback_data="language_pt-PT"),
            InlineKeyboardButton("🇪🇸 Español", callback_data="language_es-ES")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("Please select your preferred language: \nPor favor, selecione seu idioma preferido: \nPor favor, selecciona tu idioma preferido:", reply_markup=reply_markup)

async def send_edit_preferred_language_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 English", callback_data="edit_language_en-US"),
            InlineKeyboardButton("🇵🇹 Português", callback_data="edit_language_pt-PT"),
            InlineKeyboardButton("🇪🇸 Español", callback_data="edit_language_es-ES")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("Please select your preferred language: \nPor favor, selecione seu idioma preferido: \nPor favor, selecciona tu idioma preferido:", reply_markup=reply_markup)

async def send_main_menu(sender, user):
    keyboard = [
        [
            InlineKeyboardButton("📋 " + t("new_task", user.language), callback_data="menu_new_task"),
            InlineKeyboardButton("📊 " + t("my_progress", user.language), callback_data="menu_progress")
        ],
        [
            InlineKeyboardButton("🎯 " + t("my_goals", user.language), callback_data="menu_goals"),
            InlineKeyboardButton("📁 " + t("my_projects", user.language), callback_data="menu_projects")
        ],
        [
            InlineKeyboardButton("✅ " + t("my_tasks", user.language), callback_data="menu_tasks"),
            InlineKeyboardButton("⚙️ " + t("settings", user.language), callback_data="menu_settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(
        t("welcome_back", user.language).format(nickname=user.nickname),
        reply_markup=reply_markup
    )
    await sender.reply_text("_", reply_markup=MAIN_MENU_KEYBOARD)

async def send_goals_list(sender, goals, language="en-US"):
    keyboard = []
    for goal in sorted(goals, key=lambda goal: goal.name):
        if goal.status == "completed":
            keyboard.append([InlineKeyboardButton(f"🏁 {goal.name} ✅", callback_data=f"goal_projects_{goal.id}")])
            keyboard.append([
                InlineKeyboardButton("🔄 " + t("btn_reopen", language), callback_data=f"reopen_goal_{goal.id}"),
                InlineKeyboardButton("🗑️ " + t("btn_delete", language), callback_data=f"delete_goal_{goal.id}"),
                InlineKeyboardButton("📁 " + t("btn_projects", language), callback_data=f"goal_projects_{goal.id}")
            ])
        else:
            keyboard.append([InlineKeyboardButton(f"🎯 {goal.name}", callback_data=f"goal_projects_{goal.id}")])
            keyboard.append([
                InlineKeyboardButton("✏️ " + t("btn_edit", language), callback_data=f"edit_goal_{goal.id}"),
                InlineKeyboardButton("🗑️ " + t("btn_delete", language), callback_data=f"delete_goal_{goal.id}"),
                InlineKeyboardButton("📁 " + t("btn_projects", language), callback_data=f"goal_projects_{goal.id}")
            ])
    keyboard.append([InlineKeyboardButton(t("btn_new_goal", language), callback_data="new_goal")])
    keyboard.append([InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("my_goals", language), reply_markup=reply_markup)
    await sender.reply_text("_", reply_markup=MAIN_MENU_KEYBOARD)

async def send_projects_list(sender, projects, language="en-US"):
    keyboard = []
    for project in sorted(projects, key=lambda project: project.name):
        if project.status == "completed":
            keyboard.append([InlineKeyboardButton(f"🏁 {project.name} ✅", callback_data=f"project_details_{project.id}")])
            keyboard.append([
                InlineKeyboardButton("🔄 " + t("btn_reopen", language), callback_data=f"reopen_project_{project.id}"),
                InlineKeyboardButton("🗑️ " + t("btn_delete", language), callback_data=f"delete_project_{project.id}"),
                InlineKeyboardButton("✅ " + t("btn_tasks", language), callback_data=f"project_tasks_{project.id}")
            ])
        else:
            keyboard.append([InlineKeyboardButton(f"📁 {project.name}", callback_data=f"project_details_{project.id}")])
            keyboard.append([
                InlineKeyboardButton("✏️ " + t("btn_edit", language), callback_data=f"edit_project_{project.id}"),
                InlineKeyboardButton("🗑️ " + t("btn_delete", language), callback_data=f"delete_project_{project.id}"),
                InlineKeyboardButton("✅ " + t("btn_tasks", language), callback_data=f"project_tasks_{project.id}"),
                InlineKeyboardButton("🏁 " + t("btn_complete", language), callback_data=f"complete_project_{project.id}")
            ])
    keyboard.append([InlineKeyboardButton(t("btn_new_project", language), callback_data="new_project")])
    keyboard.append([InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("my_projects", language), reply_markup=reply_markup)
    await sender.reply_text("_", reply_markup=MAIN_MENU_KEYBOARD)

async def send_tasks_list(sender, tasks, language="en-US"):
    keyboard = []
    for task in sorted(tasks, key=lambda task: task.title):
        keyboard.append([InlineKeyboardButton(f"✅ {task.title} - {task.status}", callback_data=f"task_{task.id}")])
        keyboard.append([
            InlineKeyboardButton("☑️ " + t("btn_complete", language), callback_data=f"complete_task_{task.id}"),
            InlineKeyboardButton("🔄 " + t("btn_reschedule", language), callback_data=f"reschedule_task_{task.id}"),
            InlineKeyboardButton("🗑️ " + t("btn_delete", language), callback_data=f"delete_task_{task.id}")
        ])
    keyboard.append([InlineKeyboardButton(t("btn_new_task", language), callback_data="new_task")])
    keyboard.append([InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("my_tasks", language), reply_markup=reply_markup)
    await sender.reply_text("_", reply_markup=MAIN_MENU_KEYBOARD)

async def send_edit_project_menu(sender, project, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton("📝 " + t("btn_name", language), callback_data=f"eproject_name_{project.id}"),
            InlineKeyboardButton("📄 " + t("btn_description", language), callback_data=f"eproject_desc_{project.id}"),
            InlineKeyboardButton("⏰ " + t("btn_due_date", language), callback_data=f"eproject_due_date_{project.id}")
        ],
        [
            InlineKeyboardButton("⏱️ " + t("btn_time_spent", language), callback_data=f"eproject_time_{project.id}"),
            InlineKeyboardButton("🔁 " + t("btn_frequency", language), callback_data=f"eproject_frequency_{project.id}")
        ],
        [InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="menu_projects")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(f"✏️ {t('edit_project', language)}: {project.name}", reply_markup=reply_markup)

async def send_confirmation_prompt(sender, action, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_yes", language), callback_data=f"confirm_{action}"),
            InlineKeyboardButton(t("btn_no", language), callback_data=f"cancel_{action}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t(f"confirm_{action}", language), reply_markup=reply_markup)

async def send_edit_goal_menu(sender, goal, language="en-US"):
    keyboard = [
        [
            InlineKeyboardButton("📝 " + t("btn_name", language), callback_data=f"egoal_name_{goal.id}"),
            InlineKeyboardButton("📄 " + t("btn_description", language), callback_data=f"egoal_desc_{goal.id}"),
            InlineKeyboardButton("⭐ " + t("btn_importance", language), callback_data=f"egoal_importance_{goal.id}")
        ],
        [InlineKeyboardButton("❌ " + t("btn_cancel", language), callback_data="menu_goals")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(f"✏️ {t('edit_goal', language)}: {goal.name}", reply_markup=reply_markup)

async def send_settings_menu(sender, user):
    keyboard = [
        [
            InlineKeyboardButton("👤 " + t("btn_edit_nickname", user.language), callback_data="settings_nickname"),
            InlineKeyboardButton("🌍 " + t("btn_edit_language", user.language), callback_data="settings_language")
        ],
        [InlineKeyboardButton("❌ " + t("btn_cancel", user.language), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(t("settings", user.language), reply_markup=reply_markup)
    await sender.reply_text("_", reply_markup=MAIN_MENU_KEYBOARD)