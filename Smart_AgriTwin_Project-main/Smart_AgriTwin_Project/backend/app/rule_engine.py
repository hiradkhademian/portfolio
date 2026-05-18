import json
from datetime import datetime
from sqlalchemy import or_

from .models import Rule, Alert, Zone, Device, db

def parse_condition(condition_str):
    try:
        return json.loads(condition_str)
    except Exception:
        return None

def _get_value_from_path(obj, path):
    parts = path.split(".")
    cur = obj
    for p in parts:
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return None
    return cur

def eval_simple(cond, context):
    field = cond.get("field")
    op = cond.get("op")
    value = cond.get("value")

    left = _get_value_from_path(context, field)
    if left is None:
        return False

    try:
        lf = float(left)
        rf = float(value)

        if op == ">": return lf > rf
        if op == "<": return lf < rf
        if op == ">=": return lf >= rf
        if op == "<=": return lf <= rf
        if op == "==": return lf == rf
        if op == "!=": return lf != rf
    except:
        return False

    return False

def eval_condition(cond, context):
    if "and" in cond:
        return all(eval_condition(c, context) for c in cond["and"])
    if "or" in cond:
        return any(eval_condition(c, context) for c in cond["or"])
    return eval_simple(cond, context)

def evaluate_rules_for_telemetry(zone, device, telemetry):
    rules = Rule.query.filter(
        Rule.enabled == True,
        or_(Rule.zone_id == zone.id, Rule.zone_id.is_(None))
    ).all()

    # FIX: context without nested "payload"
    context = {
        "temperature": telemetry.temperature,
        "humidity": telemetry.humidity,
        "soil_moisture": telemetry.soil_moisture,
        "ph": telemetry.ph,
        "ec": telemetry.ec,
        "device": {"id": device.id, "device_uid": device.device_uid},
        "zone": {"id": zone.id, "name": zone.name}
    }

    for r in rules:
        cond = parse_condition(r.condition)
        if cond and eval_condition(cond, context):
            perform_action(r, context, telemetry)

def perform_action(rule, context, telemetry):
    if "critical" in rule.action:
        severity = "critical"
    elif "warn" in rule.action:
        severity = "warning"
    else:
        severity = "info"

    zone_id = context["zone"]["id"]
    device_id = context["device"]["id"]
    zone = Zone.query.get(zone_id)

    alert = Alert(
        rule_id=rule.id,
        zone_id=zone_id,
        device_id=device_id,
        farm_id=zone.farm_id if zone else None,
        severity=severity,
        message=f"Rule '{rule.name}' triggered: {rule.action}",
        timestamp=datetime.utcnow(),
        read=False
    )

    db.session.add(alert)
    db.session.commit()

    print("[ALERT CREATED]", alert.message)