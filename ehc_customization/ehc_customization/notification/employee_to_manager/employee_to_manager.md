<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notification: Employee Response</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 20px auto; background-color: #f4f4f4; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <div style="background-color: #007bff; color: #fff; padding: 10px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">Notification: Employee Response</h2>
        </div>
        <div style="padding: 20px;">
            <p>Dear {{doc.user}},</p>
            <p>This is to inform you that {{doc.employee}} has replied to your message regarding Late Entry.</p>
            <p>Please review the response at your earliest convenience.</p>
            <p>Thank you.</p>
        </div>
    </div>
</body>
</html>
