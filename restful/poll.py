from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class Poll(BaseModel):
    name: str
    votes: Dict[str, int]

poll = {"poll 1": Poll(name="poll 1", votes={"option 1": 0, "option 2": 0})}

@app.get("/v1/poll/{poll_id}")
async def get_poll(poll_id: str):
    return poll.get(poll_id, {"error": "Poll not found"})

@app.put("/v1/poll/{poll_id}")
async def create_poll(poll_id: str, options: List[str] = Body(...)):
    if poll_id in poll:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT)

    poll[poll_id] = Poll(name=poll_id, votes={option: 0 for option in options})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Poll created"})

@app.patch("/v1/poll/{poll_id}")
async def vote_poll(poll_id: str, option: str = Body(...)):
    if poll_id not in poll:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)

    if option not in poll[poll_id].votes:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Option not found"})

    poll[poll_id].votes[option] += 1
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Vote counted"})

@app.delete("/v1/poll/{poll_id}")
async def delete_poll(poll_id: str):
    if poll_id in poll:
        del poll[poll_id]
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Poll deleted"})
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Poll not found"})
