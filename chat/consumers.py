import asyncio
import json
import parmed as pmd

from channels.generic.websocket import AsyncWebsocketConsumer

from chatgpdb import settings
from .pdbprocessor import process_pdb_file, describe_structure
from .gpt2 import global_solver


class PDBConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self._pdb_id = self.scope["url_route"]["kwargs"]["pdb_id"]

        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "message": f"Let me see what I can find out about {self._pdb_id}...\n\n",
                    "first": True,
                }
            )
        )

        try:
            struct = await process_pdb_file(self._pdb_id)
        except OSError as err:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": f"Silly rabbit, {str(err).split(';')[0].strip()}. Tricks are for kids!"
                    }
                )
            )
            return
        except ValueError as err:
            await self.send(text_data=json.dumps({"message": str(err)}))
            return
        except pmd.exceptions.ParmedError as err:
            message = f"ParmEd had some trouble with {self._pdb_id} ({str(err)}). Try another PDB."
            await self.send(text_data=json.dumps({"message": message}))
            return
        except Exception as err:
            await self.send(
                text_data=json.dumps(
                    {"message": f"Something went wrong: {err}. Try a different PDB."}
                )
            )
            return

        description, prompt = describe_structure(struct, self._pdb_id)

        await self.send(text_data=json.dumps({"message": f"{description}\n\n"}))

        output = await global_solver.generate(
            prompt, settings.CHATGPDB_RESPONSE_WORD_COUNT
        )

        await self.send(text_data=json.dumps({"message": output}))

        await asyncio.sleep(1)
        await self.send(
            text_data=json.dumps(
                {"message": "\n\nWhen you publish these results, please cite ChatGPDB."}
            )
        )
