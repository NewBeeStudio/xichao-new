<%@ WebHandler Language="c#" Class="CropImage" Debug="true" %>

using System;
using System.Web;
using System.Drawing;
using System.IO;

public class CropImage : IHttpHandler
{
    public void ProcessRequest(HttpContext context)
    {
        string imgPath = Convert.ToString(context.Request["p"]);
        float zoomLevel = Convert.ToSingle(context.Request["z"]);
        int top = Convert.ToInt32(context.Request["t"]);
        int left = Convert.ToInt32(context.Request["l"]);
        int width = Convert.ToInt32(context.Request["w"]);
        int height = Convert.ToInt32(context.Request["h"]);
        context.Response.ContentType = "image/jpeg";
        Crop(HttpContext.Current.Server.MapPath(imgPath), zoomLevel, top, left, width, height).WriteTo(context.Response.OutputStream);
    }

    public MemoryStream Crop(string imgPath, float zoomLevel, int top, int left, int width, int height)
    {
        Image img = Image.FromFile(imgPath);
        Bitmap bitmap = new Bitmap(width, height);
        Graphics g = Graphics.FromImage(bitmap);
        g.DrawImage(img, new Rectangle(0, 0, width, height), new Rectangle((int)(left / zoomLevel), (int)(top / zoomLevel), (int)(width / zoomLevel), (int)(height / zoomLevel)), GraphicsUnit.Pixel);
        MemoryStream ms = new MemoryStream();
        bitmap.Save(ms, System.Drawing.Imaging.ImageFormat.Jpeg);
        img.Dispose();
        g.Dispose();
        bitmap.Dispose();
        return ms;
    }

    public bool IsReusable
    {
        get
        {
            return false;
        }
    }
}