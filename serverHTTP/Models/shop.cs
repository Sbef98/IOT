using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace serverHTTP.Models
{
    public class Temperature
    {
        //[Key]
        //[DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int id { get; set; }
        public double temperature { get; set; }
        public Temperature(){
            Random rnd = new Random();
            id = rnd.Next();
            temperature = rnd.NextDouble() % 35;
        }
    }
}