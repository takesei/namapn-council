import type * as ff from "@google-cloud/functions-framework";
import { auth, drive } from "@googleapis/drive";
import type { HttpFunction } from "@google-cloud/functions-framework";
import { build as buildXlsx } from "node-xlsx";
import { parse as parseCsv } from "csv-parse/sync";
import { Readable } from "node:stream";

export const updateSpreadSheet: HttpFunction = async (
	req: ff.Request,
	res: ff.Response,
) => {
	const googleAuth = new auth.GoogleAuth({
		scopes: ["https://www.googleapis.com/auth/drive"],
	});
	const driveClient = drive({
		version: "v3",
		auth: googleAuth,
	});

	const fileId = req.body.file_id;
	if (!fileId) {
		res.send("bodyにfile_idを指定してください");
		return;
	}

	const fileContents = req.body.file_contents;
	if (!fileContents) {
		res.send("bodyにfile_contentsを指定してください");
		return;
	}

	console.log(`変更対象のファイルID: ${fileId}`);

	const parsedCsv = parseCsv(Buffer.from(fileContents)) as string[][];

	const xlsxData = buildXlsx([{ data: parsedCsv, name: "", options: {} }]);
	try {
		await driveClient.files.update({
			fileId,
			supportsAllDrives: true,
			requestBody: {
				mimeType:
					"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			},
			media: {
				body: Readable.from(xlsxData),
				mimeType:
					"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			},
			uploadType:
				"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		});

		res.status(200).send();
	} catch (e: unknown) {
		console.log(e);
		res.status(500).send(`エラーが起こりました．error: ${e}`);
	}
};
