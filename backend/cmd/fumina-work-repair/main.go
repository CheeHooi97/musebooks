package main

import (
 "encoding/json"
 "flag"
 "fmt"
 "os"
 "musebooks/config"
 "musebooks/database"
 "musebooks/model"
 "gorm.io/gorm"
)

type member struct { WorkID string `json:"workId"`; EditionID string `json:"editionId"`; Title string `json:"title"`; Publisher string `json:"publisher"`; Format string `json:"format"` }
type group struct { WorkID string `json:"workId"`; Title string `json:"title"`; Members []member `json:"members"` }

func main() {
 apply := flag.Bool("apply", false, "Apply reviewed work grouping atomically; retain all editions and offers")
 manifest := flag.String("manifest", "../scraper/fumina-suzuki-work-identities.json", "Reviewed work identity map")
 flag.Parse()
 data, err := os.ReadFile(*manifest); if err != nil { panic(err) }
 var plan struct { Model string `json:"model"`; Groups []group `json:"groups"` }; if err=json.Unmarshal(data,&plan); err!=nil { panic(err) }
 if plan.Model != "鈴木ふみ奈" || len(plan.Groups)==0 { panic("unexpected repair scope") }
 config.LoadConfig(); db,err:=database.Open(!*apply,false); if err!=nil { panic(err) }
 err=db.Transaction(func(tx *gorm.DB) error {
  for _,g:=range plan.Groups {
   var canonical model.Work
   if err:=tx.First(&canonical,"id = ?",g.WorkID).Error;err!=nil{return err}
   if canonical.OriginalTitle!=g.Title || canonical.OriginCode!="JP" {return fmt.Errorf("canonical work changed: %s",g.WorkID)}
   for _,m:=range g.Members {
    var w model.Work; var e model.Edition
    if err:=tx.First(&w,"id = ?",m.WorkID).Error;err!=nil{return err}
    if err:=tx.First(&e,"id = ?",m.EditionID).Error;err!=nil{return err}
    if w.OriginalTitle!=m.Title || w.OriginCode!="JP" || w.FeaturedNames!=canonical.FeaturedNames || e.Publisher!=m.Publisher || e.Format!=m.Format || (e.WorkID!=m.WorkID && e.WorkID!=g.WorkID) {return fmt.Errorf("reviewed identity changed: %s",m.EditionID)}
    if m.WorkID==g.WorkID {continue}
    var unexpected int64
    if err:=tx.Model(&model.Edition{}).Where("work_id = ? AND id <> ?",m.WorkID,m.EditionID).Count(&unexpected).Error;err!=nil{return err}
    if unexpected!=0 {return fmt.Errorf("work gained unreviewed editions: %s",m.WorkID)}
    if *apply {
     if err:=tx.Model(&model.Edition{}).Where("id = ?",e.ID).Update("work_id",g.WorkID).Error;err!=nil{return err}
     if err:=tx.Exec(`INSERT INTO work_people (work_id,person_id,role,credited_name,credit_source,created_at,updated_at) SELECT ?,person_id,role,credited_name,credit_source,created_at,updated_at FROM work_people WHERE work_id=? ON CONFLICT DO NOTHING`,g.WorkID,m.WorkID).Error;err!=nil{return err}
     if err:=tx.Model(&model.Work{}).Where("id = ?",m.WorkID).Update("status","superseded").Error;err!=nil{return err}
    }
   }
   fmt.Printf("Reviewed %s (%d source records)\n",g.Title,len(g.Members))
  }
  return nil
 });if err!=nil{panic(err)}
 fmt.Printf("Validated %d photobook groups; applied=%v; editions, listings and observations retained\n",len(plan.Groups),*apply)
}
