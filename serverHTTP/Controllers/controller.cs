using System.Collections;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using serverHTTP.Models;

namespace TodoApi.Controllers
{
    [Route("api/[controller]")]
    public class controllerController : Controller
    {


        [HttpGet]
        public IEnumerable GetAll()
        {
            Temperature t = new Temperature();
            Temperature t1 = new Temperature();
            Temperature t2 = new Temperature();
            Temperature[] ts = {t,t1,t2};
            return ts;
        }

        // [HttpGet("{id}", Name = "GetTodo")]
        // public IActionResult GetById(long id)
        // {
        //     var item = TodoItems.Find(id);
        //     if (item == null)
        //     {
        //         return NotFound();
        //     }
        //     return new ObjectResult(item);
        // }

        // [HttpPost]
        // public IActionResult Create([FromBody] TodoItem item)
        // {
        //     if (item == null)
        //     {
        //         return BadRequest();
        //     }
        //     TodoItems.Add(item);
        //     return CreatedAtRoute("GetTodo", new { id = item.Key }, item);
        // }

        // [HttpPut("{id}")]
        // public IActionResult Update(long id, [FromBody] TodoItem item)
        // {
        //     if (item == null || item.Key != id)
        //     {
        //         return BadRequest();
        //     }

        //     var todo = TodoItems.Find(id);
        //     if (todo == null)
        //     {
        //         return NotFound();
        //     }

        //     todo.Name = item.Name;
        //     todo.IsComplete = item.IsComplete;

        //     TodoItems.Update(todo);
        //     return new NoContentResult();
        // }

        // [HttpDelete("{id}")]
        // public IActionResult Delete(long id)
        // {
        //     var todo = TodoItems.Find(id);
        //     if (todo == null)
        //     {
        //         return NotFound();
        //     }

        //     TodoItems.Remove(id);
        //     return new NoContentResult();
        // }
    }
}