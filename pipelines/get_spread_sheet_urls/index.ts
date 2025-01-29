import * as ff from "@google-cloud/functions-framework";
import { drive } from "@googleapis/drive";
import { google } from "googleapis";
import type { HttpFunction } from "@google-cloud/functions-framework";

export const getSpreadSheetUrls: HttpFunction =  async (req: ff.Request, res: ff.Response) => {
  const credentials = await google.auth.getCredentials();
  const driveClient = drive({
    version: "v3",
    auth: JSON.stringify(credentials),
  });

  try {
    const fileResponse = await driveClient.files.list({
      // TODO: reqからdriveのフォルダIDを取得するようにする
      q: "1-jfXdav0UHKDo28-fYthHbEx674kbsG3",
    });
    const files = fileResponse.data.files;
    if (!files) {
      res.send("レスポンスがありません");
      return;
    }
    if (files.length === 0) {
      res.send("ファイルがありません");
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

    res.send(JSON.stringify(spreadSheetUrls));
  } catch(e: unknown) {
    res.send(`エラーが起こりました．error: ${e}`);
  }
};
