import * as ff from "@google-cloud/functions-framework";
import { drive } from "@googleapis/drive";
import type { HttpFunction } from "@google-cloud/functions-framework";

export const getSpreadSheetUrls: HttpFunction =  async (req: ff.Request, res: ff.Response) => {
  const DRIVE_API_KEY = process.env.DRIVE_API_KEY;
  const driveClient = drive({
    version: "v3",
    auth: DRIVE_API_KEY,
  });

  const folderId = req.query['folder_id'];
  if (!folderId) {
    res.send("query parameterにfolder_idを指定してください");
    return;
  }

  console.log(`取得対象のフォルダID: ${folderId}`);

  try {
    const fileResponse = await driveClient.files.list({
      q: `'${folderId}' in parents and trashed = false`,
    });
    const files = fileResponse.data.files;
    if (!files) {
      res.json([]);
      return;
    }
    if (files.length === 0) {
      res.json([]);
    }

    const spreadSheetUrls = files.reduce((acc, curr) => {
      if (!curr.id || !curr.name) {
        return acc;
      }

      return {
        ...acc,
        [curr.id ?? ""]: curr.name,
      }
    }, {});

    res.status(200).json(spreadSheetUrls);
  } catch(e: unknown) {
    res.status(500).send(`エラーが起こりました．error: ${e}`);
  }
};
