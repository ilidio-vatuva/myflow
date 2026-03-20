from oauth import generate_oauth_url
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_oauth_prompt(sender, telegram_user_id, message):
    auth_url = generate_oauth_url(telegram_user_id)
    keyboard = [[InlineKeyboardButton("🔗 Connect Google Calendar", url=auth_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text(message, reply_markup=reply_markup)

async def send_projects_prompt(sender, projects):
    keyboard = []
    for project in sorted(projects, key=lambda project: project.name):
        inline_keyboard = [InlineKeyboardButton(f"📋 {project.name}", callback_data=f"project_{project.id}")]
        keyboard.append(inline_keyboard)
    keyboard.append([InlineKeyboardButton("➕ New Project", callback_data="new_project")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("In which project do you want to allocate the task?🤔\n", reply_markup=reply_markup)

async def send_goals_prompt(sender, goals):
    keyboard = []
    for goal in sorted(goals, key=lambda goal: goal.name):
        inline_keyboard = [InlineKeyboardButton(f"🎯 {goal.name}", callback_data=f"goalId_{goal.id}")]
        keyboard.append(inline_keyboard)
    keyboard.append([InlineKeyboardButton("➕ New Goal", callback_data="new_goal")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("In which goal do you want to allocate the project?🤔\n", reply_markup=reply_markup)

async def send_goal_importance_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("☁️ Low", callback_data="goal_importance_1"),
            InlineKeyboardButton("⛅ Medium", callback_data="goal_importance_2"),
            InlineKeyboardButton("☀️ High", callback_data="goal_importance_3")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("How important is this goal? 🔥\n", reply_markup=reply_markup)

async def send_deadline_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("🔥 Today", callback_data="deadline_today"),
            InlineKeyboardButton("⏰ Tomorrow", callback_data="deadline_tomorrow")
        ],
        [
            InlineKeyboardButton("📅 This week", callback_data="deadline_this_week"),
            InlineKeyboardButton("🌙 This month", callback_data="deadline_this_month"),
            InlineKeyboardButton("🌊 No deadline", callback_data="deadline_none")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("📅 When is the deadline?\n", reply_markup=reply_markup)

async def send_project_daily_hours_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("⏰ 1 hour", callback_data="hours_1"),
            InlineKeyboardButton("⏰ 2 hours", callback_data="hours_2"),
            InlineKeyboardButton("⏰ 3 hours", callback_data="hours_3"),
            InlineKeyboardButton("⏰ 4 hours", callback_data="hours_4")
        ],
        [
            InlineKeyboardButton("⏰ 5 hour", callback_data="hours_5"),
            InlineKeyboardButton("⏰ 6 hours", callback_data="hours_6"),
            InlineKeyboardButton("⏰ 7 hours", callback_data="hours_7"),
            InlineKeyboardButton("⏰ 8 hours", callback_data="hours_8")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("⏳ How many time do you want to spend on this project?\n", reply_markup=reply_markup)

async def send_project_weekly_hours_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("⏰ 5 hour", callback_data="hours_5"),
            InlineKeyboardButton("⏰ 6 hours", callback_data="hours_6"),
            InlineKeyboardButton("⏰ 7 hours", callback_data="hours_7"),
            InlineKeyboardButton("⏰ 8 hours", callback_data="hours_8"),
        ],
        [
            InlineKeyboardButton("⏰ 10 hours", callback_data="hours_10"),
            InlineKeyboardButton("⏰ 20 hours", callback_data="hours_20"),
            InlineKeyboardButton("⏰ 40 hours", callback_data="hours_40")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("⏳ How many time do you want to spend on this project?\n", reply_markup=reply_markup)

async def send_project_monthly_hours_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("⏰ 20 hour", callback_data="hours_20"),
            InlineKeyboardButton("⏰ 40 hours", callback_data="hours_40"),
            InlineKeyboardButton("⏰ 60 hours", callback_data="hours_60"),
            InlineKeyboardButton("⏰ 80 hours", callback_data="hours_80")
        ],
        [
            InlineKeyboardButton("⏰ 100 hours", callback_data="hours_100"),
            InlineKeyboardButton("⏰ 150 hours", callback_data="hours_150"),
            InlineKeyboardButton("⏰ 200 hours", callback_data="hours_200")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("⏳ How many time do you want to spend on this project?\n", reply_markup=reply_markup)

async def send_project_frequency_prompt(sender):
    keyboard = [
        [
            InlineKeyboardButton("📅 Daily", callback_data="frequency_daily"),
            InlineKeyboardButton("📅 Weekly", callback_data="frequency_weekly"),
            InlineKeyboardButton("📅 Monthly", callback_data="frequency_monthly")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("📆 How often do you want to work on this project?\n", reply_markup=reply_markup)

async def send_due_date_prompt(sender):
    keyboard = [
    [
        InlineKeyboardButton("📅 1 month", callback_data="due_date_1month"),
        InlineKeyboardButton("📅 3 months", callback_data="due_date_3months"),
        InlineKeyboardButton("📅 6 months", callback_data="due_date_6months"),
    ],
    [
        InlineKeyboardButton("📅 1 year", callback_data="due_date_1year"),
        InlineKeyboardButton("🌊 No due date", callback_data="due_date_none")
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await sender.reply_text("📅 When is the due date?\n", reply_markup=reply_markup)