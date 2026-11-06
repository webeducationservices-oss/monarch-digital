"""Hand-built pages: the AI assessment, contact, and 404. Called from build.py with its globals."""

CONCEPTS = ["Fine dining", "Casual dining", "Fast casual", "Quick service", "Bar or brewery", "Cafe or bakery",
            "Private club", "Hotel or resort F&B", "Catering or events"]
LOCATIONS = ["1 location", "2 to 5", "6 to 20", "More than 20", "Opening my first"]
SEATS = ["Under 50", "50 to 100", "100 to 200", "200 plus"]
STAFF = ["Under 15", "15 to 40", "40 to 100", "100 plus"]
POS = ["Toast", "Square", "Clover", "Lightspeed", "SpotOn", "Other", "No POS yet"]
RESERVATIONS = ["OpenTable", "Resy", "SevenRooms", "Tock", "Built into my POS", "Phone and paper", "We don't take reservations"]
SCHEDULING = ["Spreadsheet or paper", "A scheduling app", "My POS", "Group texts", "Not sure"]
TRAINING = ["Shadow shifts", "Binders and handouts", "Videos", "Training software or LMS", "Nothing formal yet"]
HEADACHES = ["Labor cost", "Staff turnover", "Inconsistent training", "Slow table turns", "Kitchen pacing",
             "Food cost", "Scheduling chaos", "Team communication", "Not enough new guests", "Slow weeknights"]
PROJECTS = ["Opening a new location", "Remodel or new furniture", "New uniforms", "New menu", "Launching catering or events",
            "New software", "Nothing planned"]
CHANNELS = ["Google Business Profile", "Instagram", "Facebook", "TikTok", "Email", "Text messages", "Paid ads",
            "Third-party delivery apps", "None yet"]
OWNERS = ["I do it myself", "A staff member", "An agency", "Nobody right now"]
GOALS = ["More covers", "Higher check average", "Better reviews", "Lower labor cost", "Better staff retention",
         "Open another location", "Grow catering or events"]
ROLES = ["Owner", "General manager", "Chef", "Operating partner", "Other"]


def _chips(name, options, multi=False, required=False):
    kind = "checkbox" if multi else "radio"
    req = ' data-required="1"' if required else ""
    cells = "".join(
        f'<label class="chip"><input type="{kind}" name="{name}" value="{o}"><span>{o.replace("&", "&amp;")}</span></label>'
        for o in options)
    return f'<div class="chips" data-group="{name}"{req}>{cells}</div>'


def _q(label, inner, hint=""):
    h = f' <span style="font-weight:500;color:var(--g500)">{hint}</span>' if hint else ""
    return f'<div class="q"><div class="q-label">{label}{h}</div>{inner}</div>'


def assessment(g):
    esc, icon, SITE = g["esc"], g["icon"], g["SITE"]
    hero = {"eyebrow": "Free AI Restaurant Assessment", "h1": "See Where Your Restaurant Is Leaving Money on the Table",
            "sub": "Answer about a dozen questions and tell us your restaurant's name. Our AI reads your answers, your Google listing and reviews, and your website, then shows you where operations and marketing can improve. Christy follows up personally.",
            "primary_cta": {"label": "Start the Assessment", "href": "#start"},
            "secondary_cta": {"label": "Talk to Christy", "href": "/contact/"}}
    preload, hero_html, crumb_schema = g["page_hero"]("assessment", hero, [("Home", "/"), ("Free AI Assessment", "/ai-assessment/")])
    faq = [
        {"q": "Is the assessment really free?", "a": "Yes. There's no cost and no obligation. You get the evaluation on this page and by email, and Christy reaches out to talk it through if you'd like."},
        {"q": "What does the AI look at?", "a": "Your answers, your public Google Business Profile (rating, review count, and recent reviews), and your public website (menu, ordering, reservations, mobile basics, and search signals). It doesn't log in anywhere or touch your POS."},
        {"q": "How long does it take?", "a": "About three minutes to answer the questions. The AI usually finishes its evaluation in under a minute."},
        {"q": "What happens with my information?", "a": "Christy receives your answers and your report so she can follow up. We don't sell or share your information."},
        {"q": "Is the AI always right?", "a": "It's a fast, evidence-based first look, and every finding shows what it was based on. A person reviews it with you before anything is decided. A person always confirms anything that books, publishes, or sends."},
    ]
    faq_html, faq_schema = g["faq_section"](faq, 1)
    steps = g["render_section"]({"type": "steps", "label": "How it works", "h2": "From Questions to a Plan in Minutes",
                                 "items": [{"title": "Answer", "text": "A dozen quick questions about your restaurant, your systems, and your goals."},
                                           {"title": "We look you up", "text": "The AI reads your Google listing, recent reviews, and website for real evidence."},
                                           {"title": "AI evaluates", "text": "Scores across six areas, findings with evidence, quick wins, and a 90-day plan."},
                                           {"title": "Christy follows up", "text": "A personal call to walk through it. We do the work. You guide the process."}]}, 0, "assessment")
    features = g["render_section"]({"type": "features", "label": "What you get", "h2": "A Clear Picture of Your Operation",
                                    "items": [{"icon": "target", "title": "Six scores", "text": "Operations, team and training, guest experience, marketing, reviews, and website."},
                                              {"icon": "search", "title": "Findings with evidence", "text": "Every finding shows what it's based on, from your answers, your reviews, or your site."},
                                              {"icon": "zap", "title": "Quick wins", "text": "Practical moves you can make in the next 30 days, plus a 90-day plan for the bigger ones."},
                                              {"icon": "mail", "title": "Your report by email", "text": "A copy lands in your inbox so you can share it with your partners or GM."}]}, 1, "assessment")

    step1 = f"""<fieldset class="q-step active" data-step="1"><legend class="sr-only">Your restaurant</legend>
      <h2>Your restaurant</h2><p>So the AI can find your Google listing and website.</p>
      <div class="form-row"><div class="form-group"><label for="a-name">Restaurant name *</label><input id="a-name" name="restaurant_name" maxlength="120" required autocomplete="organization"></div>
      <div class="form-group"><label for="a-city">City and state *</label><input id="a-city" name="city_state" maxlength="80" required placeholder="Tampa, FL"></div></div>
      <div class="form-group"><label for="a-web">Website <span style="font-weight:500;color:var(--g500)">(optional, we'll look it up if blank)</span></label><input id="a-web" name="website" maxlength="200" inputmode="url" placeholder="yourrestaurant.com"></div>
      {_q("What kind of place is it? *", _chips("concept", CONCEPTS, required=True))}
      {_q("How many locations? *", _chips("locations", LOCATIONS, required=True))}
      <div class="form-row">{_q("Seats per location", _chips("seats", SEATS))}{_q("Team size", _chips("staff", STAFF))}</div>
    </fieldset>"""
    step2 = f"""<fieldset class="q-step" data-step="2"><legend class="sr-only">Operations</legend>
      <h2>How you run things</h2><p>No wrong answers. This tells us where the friction is.</p>
      {_q("Point of sale", _chips("pos", POS))}
      {_q("Reservations", _chips("reservations", RESERVATIONS))}
      {_q("How do you build the staff schedule?", _chips("scheduling", SCHEDULING))}
      {_q("How do new hires learn the job?", _chips("training", TRAINING))}
      {_q("Biggest headaches right now *", _chips("headaches", HEADACHES, multi=True, required=True), "(pick up to 3)")}
      {_q("Anything coming up?", _chips("projects", PROJECTS, multi=True))}
    </fieldset>"""
    step3 = f"""<fieldset class="q-step" data-step="3"><legend class="sr-only">Marketing</legend>
      <h2>Getting found</h2><p>Where guests hear about you today.</p>
      {_q("Marketing you use now", _chips("channels", CHANNELS, multi=True))}
      {_q("Who handles marketing?", _chips("marketing_owner", OWNERS))}
      {_q("Your top goal for the next 12 months *", _chips("goal", GOALS, required=True))}
      <div class="form-group"><label for="a-notes">Anything else we should know? <span style="font-weight:500;color:var(--g500)">(optional)</span></label>
      <textarea id="a-notes" name="notes" maxlength="600" placeholder="A problem you want solved, a project you're planning, a question for Christy."></textarea></div>
    </fieldset>"""
    step4 = f"""<fieldset class="q-step" data-step="4"><legend class="sr-only">Where to send it</legend>
      <h2>Where should we send your report?</h2><p>You'll see it here in about a minute, and a copy goes to your inbox.</p>
      <div class="form-row"><div class="form-group"><label for="a-first">First name *</label><input id="a-first" name="first_name" maxlength="60" required autocomplete="given-name"></div>
      <div class="form-group"><label for="a-last">Last name *</label><input id="a-last" name="last_name" maxlength="60" required autocomplete="family-name"></div></div>
      <div class="form-row"><div class="form-group"><label for="a-email">Email *</label><input id="a-email" type="email" name="email" maxlength="120" required autocomplete="email"></div>
      <div class="form-group"><label for="a-phone">Phone</label><input id="a-phone" type="tel" name="phone" maxlength="30" autocomplete="tel"></div></div>
      {_q("Your role", _chips("role", ROLES))}
      <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
      <p class="fine">By running the assessment you agree that Christy at Monarch Digital may contact you about your results.</p>
    </fieldset>"""

    form = f"""<form id="assessForm" class="form-card" novalidate>
      <div class="assess-steps-nav" aria-hidden="true"><span class="on">1. Restaurant</span><span>2. Operations</span><span>3. Marketing</span><span>4. Your report</span></div>
      <div class="assess-progress" aria-hidden="true"><span></span></div>
      {step1}{step2}{step3}{step4}
      <div class="q-error" id="qError" role="alert"></div>
      <div class="q-nav"><button type="button" class="btn btn-line" id="qBack" hidden>Back</button>
      <button type="button" class="btn btn-gold" id="qNext">Next {icon("arrow-right", "icon")}</button>
      <button type="submit" class="btn btn-gold" id="qSubmit" hidden>{icon("zap", "icon")}Run My Assessment</button></div>
    </form>
    <div class="assess-working form-card" id="assessWorking" aria-live="polite">
      <div class="spinner"></div><h2 style="font-size:26px;margin-bottom:6px">Evaluating <span id="wName">your restaurant</span></h2>
      <p style="color:var(--g600)">This usually takes under a minute.</p>
      <ul class="working-steps"><li data-w="1">{icon("check-circle", "icon")}Reading your answers</li><li data-w="2">{icon("check-circle", "icon")}Checking your Google listing and reviews</li>
      <li data-w="3">{icon("check-circle", "icon")}Scanning your website</li><li data-w="4">{icon("check-circle", "icon")}Writing your evaluation</li></ul>
    </div>
    <div class="report" id="assessReport" aria-live="polite"></div>"""

    v_js = g["asset_version"]("assessment.js")
    extra = f'  <script src="/assessment.js?v={v_js}" defer></script>\n'
    schema = "\n  ".join(g["ld"](s) for s in (crumb_schema, faq_schema))
    page = g["head"]("Free AI Restaurant Assessment | Monarch Digital",
                     "Free AI restaurant assessment: our AI reads your answers, Google reviews, and website, then scores operations and marketing with quick wins. Christy follows up.",
                     "/ai-assessment/", g["abs_url"]("/images/rebrand/og/assessment-hero.jpg"), schema, preload=preload, extra=extra)
    page += g["header"]("assessment") + f"""  <main id="main">
{hero_html}  <section class="bg-cream" id="start"><div class="container assess-wrap">{form}</div></section>
{features}{steps}{faq_html}{g["cta_band"]({"h2": "Rather Talk It Through First?", "sub": "Christy is happy to walk through your restaurant on a call before you run anything.", "primary_cta": {"label": "Talk to Christy", "href": "/contact/"}, "secondary_cta": {"label": "See Our Work", "href": "/case-study/"}})}  </main>
""" + g["footer"]()
    return page, "ai-assessment.html"


def contact(g):
    esc, icon, SITE = g["esc"], g["icon"], g["SITE"]
    hero = {"eyebrow": "Contact", "h1": "Let's Talk About Your Restaurant",
            "sub": "Tell us what you're working on. Christy reads every message and replies within one business day.",
            "primary_cta": {"label": "Send a Message", "href": "#contact-form"},
            "secondary_cta": {"label": "Get Your Free AI Assessment", "href": "/ai-assessment/"}}
    preload, hero_html, crumb_schema = g["page_hero"]("contact", hero, [("Home", "/"), ("Contact", "/contact/")])
    options = "".join(f"<option>{t}</option>" for t in
                      ["Custom software or apps", "AI assistants", "Training and custom LMS", "Marketing", "Scheduling and labor",
                       "Operations consulting", "Furniture and FF&amp;E", "Uniform programs", "Multi-location rollout", "Opening a new restaurant", "Something else"])
    form = f"""<form action="https://myaieditor.com/api/form-notify" method="POST" data-ajax class="form-card" id="contact-form">
      <div class="form-fields">
        <input type="hidden" name="site_slug" value="{SITE['form_slug']}">
        <input type="hidden" name="form_type" value="contact">
        <input type="hidden" name="recaptcha_token" value="">
        <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
        <h2 style="font-size:26px;margin-bottom:6px">Send a message</h2>
        <p style="color:var(--g600);margin-bottom:22px">We'll get back to you within one business day.</p>
        <div class="form-row"><div class="form-group"><label for="c-first">First name *</label><input id="c-first" name="first_name" required autocomplete="given-name"></div>
        <div class="form-group"><label for="c-last">Last name *</label><input id="c-last" name="last_name" required autocomplete="family-name"></div></div>
        <div class="form-row"><div class="form-group"><label for="c-email">Email *</label><input id="c-email" type="email" name="email" required autocomplete="email"></div>
        <div class="form-group"><label for="c-phone">Phone</label><input id="c-phone" type="tel" name="phone" autocomplete="tel"></div></div>
        <div class="form-row"><div class="form-group"><label for="c-co">Restaurant or company</label><input id="c-co" name="company" autocomplete="organization"></div>
        <div class="form-group"><label for="c-city">City and state</label><input id="c-city" name="city_state"></div></div>
        <div class="form-group"><label for="c-topic">What can we help with?</label><select id="c-topic" name="service_type">{options}</select></div>
        <div class="form-group"><label for="c-msg">Message *</label><textarea id="c-msg" name="message" required></textarea></div>
        <button type="submit" class="btn btn-gold form-submit">Send Message</button>
        <p class="fine">Protected by reCAPTCHA. Google's <a href="https://policies.google.com/privacy">Privacy Policy</a> and <a href="https://policies.google.com/terms">Terms</a> apply.</p>
      </div>
      <div class="form-success" role="status">{icon("check-circle", "icon")}<h3>Message sent</h3>
        <p>Thank you for reaching out. Christy will get back to you within one business day. Need us sooner? Call <a href="{SITE['phone_href']}" style="color:var(--teal-text);font-weight:600">{SITE['phone']}</a>.</p></div>
      <div class="form-error" role="alert">We couldn't send that just now. Please call <a href="{SITE['phone_href']}">{SITE['phone']}</a> or email <a href="mailto:{SITE['email']}">{SITE['email']}</a> and we'll take care of it right away.</div>
    </form>"""
    body = f"""  <section class="bg-cream"><div class="container contact-grid">
    <div class="reveal">
      <div class="label">Get in touch</div>
      <h2 style="font-size:clamp(28px,3.4vw,40px);margin-bottom:16px">One Team for Everything Your Restaurant Runs On</h2>
      <p style="font-size:17.5px;color:var(--g700)">Software, AI, training, marketing, scheduling, furniture, and uniforms, handled by one white-glove team. {SITE['promise']}</p>
      <div class="contact-list">
        <a href="{SITE['phone_href']}"><span class="ci">{icon("phone", "icon")}</span>{SITE['phone']}</a>
        <a href="mailto:{SITE['email']}"><span class="ci">{icon("mail", "icon")}</span>{SITE['email']}</a>
        <div><span class="ci">{icon("map-pin", "icon")}</span>Based in {SITE['base']}. Serving restaurants nationwide.</div>
      </div>
      <div class="feature" style="margin-top:32px"><div class="feature-icon">{icon("zap", "icon")}</div>
        <h3>Not sure where to start?</h3><p>Run the free AI assessment. It scores your operations and marketing in about a minute, and Christy follows up with you personally.</p>
        <a class="card-more" href="/ai-assessment/">Get your free AI assessment {icon("arrow-right", "icon")}</a></div>
    </div>
    <div class="reveal">{form}</div>
  </div></section>
"""
    contact_schema = {"@context": "https://schema.org", "@type": "ContactPage", "url": g["abs_url"]("/contact/"), "name": "Contact Monarch Digital"}
    schema = "\n  ".join(g["ld"](s) for s in (crumb_schema, contact_schema))
    page = g["head"]("Contact Monarch Digital | Restaurant Consulting",
                     "Contact Monarch Digital about restaurant software, AI, training, marketing, scheduling, furniture, or uniforms. Based in Tampa Bay, serving restaurants nationwide.",
                     "/contact/", g["abs_url"]("/images/rebrand/og/contact-hero.jpg"), schema, preload=preload)
    page += g["header"]("contact") + f'  <main id="main">\n{hero_html}{body}  </main>\n' + g["footer"]()
    return page, "contact.html"


def notfound(g):
    icon = g["icon"]
    page = g["head"]("Page Not Found | Monarch Digital", "That page moved or never existed. Find restaurant services, the free AI assessment, and the blog here.",
                     "/404", g["abs_url"]("/images/rebrand/og/home-detail.jpg"), "")
    page = page.replace('<meta name="description"', '<meta name="robots" content="noindex">\n  <meta name="description"', 1)
    page += g["header"]() + f"""  <main id="main" class="notfound"><div>
    <div class="label" style="justify-content:center">Page not found</div>
    <h1>That page has moved</h1>
    <p style="font-size:18px;color:var(--g600);max-width:560px;margin:0 auto 32px">The link may be old or mistyped. Here are the places most people are looking for.</p>
    <div class="btn-row" style="justify-content:center"><a class="btn btn-gold" href="/">Go to the homepage</a><a class="btn btn-line" href="/services/">See our services</a>
    <a class="btn btn-line" href="/blog/">Read the blog</a></div>
  </div></main>
""" + g["footer"]()
    return page, "404.html"
