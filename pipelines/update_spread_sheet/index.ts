import * as ff from "@google-cloud/functions-framework";
import { drive } from "@googleapis/drive";
import type { HttpFunction } from "@google-cloud/functions-framework";

export const updateSpreadSheet: HttpFunction =  async (req: ff.Request, res: ff.Response) => {
  const DRIVE_API_KEY = process.env.DRIVE_API_KEY;
  const driveClient = drive({
    version: "v3",
    auth: DRIVE_API_KEY,
  });

  const fileId = req.body['file_id'];
  if (!fileId) {
    res.send("bodyにfile_idを指定してください");
    return;
  }

  const fileContents = req.body['file_contents'];
  if (!fileContents) {
    res.send("bodyにfile_contentsを指定してください");
    return;
  }

  console.log(`変更対象のファイルID: ${fileId}`);

  try {
    await driveClient.files.update({
      fileId,
      media: {
        body: fileContents,
        mimeType: "text/csv"
      }
    })

    res.status(200);
  } catch(e: unknown) {
    res.status(500).send(`エラーが起こりました．error: ${e}`);
  }
};
